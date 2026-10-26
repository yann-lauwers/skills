# The file `billit orders create` takes

Billit's own order JSON, one object:

- `OrderType`: `Invoice` (or `CreditNote`) · `OrderDirection`: `Cost` for a purchase, `Income` for a sale.
- `OrderNumber` and `Reference`: the document's number · `OrderDate`, `ExpiryDate`, `DeliveryDate`: `YYYY-MM-DD`.
- `Supplier` and `Customer`: `{"PartyID": <id>}` — the entity's own party on its side, from `billit whoami`.
- `Currency`, `CostCategoryCode` (a purchase), `ProjectID` (when the order belongs to a project).
- `OrderLines`: one entry per line — `Quantity`, `UnitPriceExcl`, `Description`, `VATPercentage`, `VentilationCode`, `TotalExcl`, `TotalVAT`, `TotalIncl`.
- `VatGroups`: one entry per VAT rate and code — `VentilationCode`, `VATPercentage`, `TotalExcl`, `TotalVAT`, `TotalIncl` — matching the lines.
- `VentilationCode` on the header, on every line and on every `VatGroups` entry; the command refuses a file missing one.
- `OrderPDF`: `{"path": "<file>"}`, a PDF. A Peppol XML from the queue: its PDF in `OrderPDF`, the XML itself in `Attachments` as `[{"path": "<the .xml>"}]` — `billit queue clear` looks for the queued file's exact bytes on the order.
