# Category and VAT code

- Category — which expense account a purchase books to: `CostCategoryCode`, listed by `billit categories list`.
- VAT code — how its VAT is treated: `VentilationCode`, from Billit's published table, cost side `https://docs.billit.be/docs/ventilation-codes-for-cost-invoices.md`, sales side `https://docs.billit.be/docs/ventilation-codes.md`.
- Both sit on the supplier, where they only prefill documents entered by hand, and on each order; `billit orders create` needs both on the order, per `order-spec.md`.
- Which treatment a document is owed → research it for that case, from the document and primary sources, and confirm it with the user before encoding; never carry one case's answer to another as a rule.
