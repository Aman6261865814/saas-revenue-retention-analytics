// Create text parameter DataFolder pointing to this project's data/processed.
// Create blank query named fnLoadCSV and paste this function.
(FileName as text, ColumnTypes as list) as table =>
let
    Raw = Csv.Document(File.Contents(DataFolder & "/" & FileName), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Raw, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, ColumnTypes, "en-US")
in Typed
