from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    # Compute on the variant itself, including before a template exists.
    can_select_product_company = fields.Boolean(
        compute="_compute_can_select_product_company",
        default=lambda self: len(self.env.companies) > 1,
    )

    @api.depends_context("allowed_company_ids", "uid")
    def _compute_can_select_product_company(self):
        can_select = len(self.env.companies) > 1
        for product in self:
            product.can_select_product_company = can_select

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if "company_id" in fields_list:
            template_id = defaults.get(
                "product_tmpl_id", self.env.context.get("default_product_tmpl_id")
            )
            defaults["company_id"] = (
                self.env["product.template"].browse(template_id).company_id.id
                if template_id
                else self.env.company.id
            )
        return defaults

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [dict(vals) for vals in vals_list]
        for vals in vals_list:
            template_id = vals.get(
                "product_tmpl_id", self.env.context.get("default_product_tmpl_id")
            )
            if template_id:
                # company_id is delegated to the template. Do not let variant
                # creation write a form/context default onto an existing product.
                # Supplying the parent explicitly also suppresses ORM defaults
                # for its inherited fields.
                vals["product_tmpl_id"] = template_id
                vals.pop("company_id", None)
            else:
                # Normalize before delegated creation: the related field's
                # inverse must not write the original value back afterwards.
                vals["company_id"] = self.env["product.template"]._get_product_creation_company_id(
                    vals.get("company_id")
                )
        return super().create(vals_list)
