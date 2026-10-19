from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

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
                vals["company_id"] = self.env.company.id
        return super().create(vals_list)
