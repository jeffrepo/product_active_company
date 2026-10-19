from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        if "company_id" in fields_list:
            defaults["company_id"] = self.env.company.id
        return defaults

    @api.model_create_multi
    def create(self, vals_list):
        # Enforce the active company for every entry point, including imports,
        # duplication and explicit empty or different company values.
        company_id = self.env.company.id
        vals_list = [dict(vals, company_id=company_id) for vals in vals_list]
        return super().create(vals_list)
