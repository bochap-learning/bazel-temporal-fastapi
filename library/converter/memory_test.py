from library.converter.memory import to_csv_stringio

def test_to_csv_stringio():
    field_names = ["column1", "column2"]
    data = [{"column1": 1, "column2": 2},{"column1": 3, "column2": 4}]
    expected = "column1,column2\r\n1,2\r\n3,4\r\n"
    assert to_csv_stringio(field_names, data).getvalue() == expected