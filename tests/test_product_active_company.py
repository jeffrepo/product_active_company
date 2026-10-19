from odoo import Command
from odoo.exceptions import AccessError
from odoo.tests import Form, TransactionCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestProductActiveCompany(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.companies = cls.env["res.company"].create([
            {"name": "Active Company A"},
            {"name": "Active Company B"},
            {"name": "Active Company C"},
        ])
        cls.company_a, cls.company_b, cls.company_c = cls.companies
        cls.user = new_test_user(
            cls.env,
            login="product_active_company_test",
            groups="base.group_user,base.group_system,base.group_multi_company",
            company_id=cls.company_a.id,
            company_ids=[Command.set(cls.companies.ids)],
        )

    def _model(self, model_name="product.template", companies=None):
        companies = companies if companies is not None else [
            self.company_b.id, self.company_a.id, self.company_c.id
        ]
        return self.env[model_name].with_user(self.user).with_context(
            allowed_company_ids=companies
        )

    def test_one_two_and_three_assigned_companies(self):
        for count in (1, 2, 3):
            assigned = self.companies[:count]
            self.user.company_ids = [Command.set(assigned.ids)]
            active = assigned[-1]
            enabled = [active.id] + (assigned - active).ids
            for model_name in ("product.template", "product.product"):
                with self.subTest(count=count, model=model_name):
                    model = self._model(model_name, enabled)
                    self.assertFalse(model.env.su)
                    self.assertEqual(model.env.user.company_id, self.company_a)
                    self.assertEqual(
                        model.default_get(["company_id"])["company_id"], active.id
                    )
                    product = model.create({"name": "Assigned companies %s" % count})
                    self.assertEqual(product.company_id, active)

    def test_switch_active_company_with_all_companies_enabled(self):
        for active in (self.company_b, self.company_c, self.company_a):
            enabled = [active.id] + (self.companies - active).ids
            for model_name in ("product.template", "product.product"):
                product = self._model(model_name, enabled).create({"name": "Switch"})
                self.assertEqual(product.company_id, active)

    def test_defaults_ignore_other_or_empty_company(self):
        for model_name in ("product.template", "product.product"):
            for company_id in (False, self.company_a.id):
                model = self._model(model_name).with_context(
                    default_company_id=company_id
                )
                self.assertEqual(
                    model.default_get(["company_id"])["company_id"], self.company_b.id
                )
                self.assertNotIn("company_id", model.default_get(["name"]))

    def test_batch_create_overrides_explicit_companies(self):
        for model_name in ("product.template", "product.product"):
            values = [
                {"name": "Missing company"},
                {"name": "Empty company", "company_id": False},
                {"name": "Other company", "company_id": self.company_a.id},
            ]
            original_values = [dict(vals) for vals in values]
            products = self._model(model_name).with_context(
                default_company_id=self.company_c.id
            ).create(values)
            self.assertEqual(len(products), 3)
            self.assertEqual(products.mapped("company_id"), self.company_b)
            self.assertEqual(values, original_values)

    def test_product_forms(self):
        for model_name, view in (
            ("product.template", "product.product_template_only_form_view"),
            ("product.product", "product.product_normal_form_view"),
        ):
            with self.subTest(model=model_name):
                with Form(self._model(model_name), view=view) as form:
                    self.assertEqual(form.company_id, self.company_b)
                    form.name = "Created in product form"
                self.assertEqual(form.record.company_id, self.company_b)

    def test_quick_create(self):
        for model_name in ("product.template", "product.product"):
            model = self._model(model_name)
            product_id, _name = model.name_create("Quick creation")
            self.assertEqual(model.browse(product_id).company_id, self.company_b)

    def test_import_uses_active_company(self):
        for model_name in ("product.template", "product.product"):
            model = self._model(model_name)
            result = model.load(
                ["name", "company_id/.id"],
                [["Imported product", str(self.company_a.id)]],
            )
            self.assertTrue(result["ids"], result["messages"])
            self.assertEqual(model.browse(result["ids"]).company_id, self.company_b)

    def test_copy_uses_active_company(self):
        for model_name in ("product.template", "product.product"):
            model = self._model(model_name)
            original = model.with_company(self.company_a).create({"name": "Original"})
            duplicate = original.with_company(self.company_b).copy()
            self.assertEqual(original.company_id, self.company_a)
            self.assertEqual(duplicate.company_id, self.company_b)

    def test_existing_template_keeps_company_when_adding_variant(self):
        for shared in (False, True):
            for use_context in (False, True):
                template = self._model().with_company(self.company_a).with_context(
                    create_product_product=False
                ).create({"name": "Existing template"})
                if shared:
                    template.company_id = False
                expected = template.company_id
                model = self._model("product.product").with_context(
                    default_company_id=self.company_b.id
                )
                values = {"company_id": self.company_b.id}
                if use_context:
                    model = model.with_context(default_product_tmpl_id=template.id)
                    self.assertEqual(
                        model.default_get(["company_id"])["company_id"], expected.id
                    )
                else:
                    values["product_tmpl_id"] = template.id
                variant = model.create(values)
                self.assertEqual(variant.product_tmpl_id, template)
                self.assertEqual(variant.company_id, expected)
                self.assertEqual(template.company_id, expected)

    def test_mixed_batch_with_new_and_existing_templates(self):
        template = self._model().with_company(self.company_a).with_context(
            create_product_product=False
        ).create({"name": "Existing template"})
        products = self._model("product.product").create([
            {"product_tmpl_id": template.id, "company_id": self.company_b.id},
            {"name": "New product", "company_id": self.company_a.id},
        ])
        self.assertEqual(products[0].company_id, self.company_a)
        self.assertEqual(products[1].company_id, self.company_b)

    def test_edit_existing_product_keeps_company(self):
        original = self._model().with_company(self.company_a).create({"name": "Original"})
        original.with_company(self.company_b).write({"name": "Edited"})
        self.assertEqual(original.company_id, self.company_a)

    def test_cannot_create_in_unauthorized_company(self):
        unauthorized = self.env["res.company"].create({"name": "Unauthorized company"})
        for model_name in ("product.template", "product.product"):
            with self.assertRaises(AccessError), self.cr.savepoint():
                self._model(model_name, [unauthorized.id]).create({"name": "Blocked"})

    def test_product_permissions_are_preserved(self):
        self.user.groups_id = [Command.set(self.env.ref("base.group_user").ids)]
        for model_name in ("product.template", "product.product"):
            with self.assertRaises(AccessError), self.cr.savepoint():
                self._model(model_name).create({"name": "No create permission"})
