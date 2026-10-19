from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # A duplicate starts with the active company unless explicitly overridden.
    company_id = fields.Many2one(copy=False)
    can_select_product_company = fields.Boolean(
        compute="_compute_can_select_product_company",
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
            defaults["company_id"] = self.env.company.id
        return defaults

    @api.model_create_multi
    def create(self, vals_list):
        enabled_companies = self.env.companies
        vals_list = [dict(vals) for vals in vals_list]
        for vals in vals_list:
            if len(enabled_companies) <= 1 or not vals.get("company_id"):
                vals["company_id"] = self.env.company.id
            elif vals["company_id"] not in enabled_companies.ids:
                raise ValidationError(_(
                    "Selecciona una de las empresas habilitadas en el selector de empresas."
                ))
        return super().create(vals_list)
