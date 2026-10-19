from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    # A duplicate starts with the active company unless explicitly overridden.
    company_id = fields.Many2one(copy=False)
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
            defaults["company_id"] = self.env.company.id
        return defaults

    @api.model
    def _get_product_creation_company_id(self, company_id=False):
        enabled_companies = self.env.companies
        if len(enabled_companies) <= 1 or not company_id:
            return self.env.company.id
        if company_id not in enabled_companies.ids:
            raise ValidationError(_(
                "Selecciona una de las empresas habilitadas en el selector de empresas."
            ))
        return company_id

    @api.model_create_multi
    def create(self, vals_list):
        vals_list = [
            dict(vals, company_id=self._get_product_creation_company_id(vals.get("company_id")))
            for vals in vals_list
        ]
        return super().create(vals_list)
