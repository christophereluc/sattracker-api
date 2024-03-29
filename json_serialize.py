def json_serialize(rows, cursor):
    data = []
    cols = [desc[0] for desc in cursor.description]
    result = []
    for row in rows:
        row = dict(zip(cols, row))
        result.append(row)
    if len(rows) == 1:
        return result[0]
    else:
        return result
