import sqlite3


with sqlite3.connect('old.sqlite3') as conn:
    cur = conn.cursor()
    cur.execute('select id, name, lft, rght, tree_id, level, prev_org_id, prev_pos_id, type_id, parent_id from letters_counterparty')

    result = cur.fetchall()
    #for row in result:
        #print(row)



with sqlite3.connect('db.sqlite3') as conn:
    for r in result:
        r = ', '.join([("'" + (str(x) + "'") if x is not None else 'NULL') for x in r])
        print(r)
        cur = conn.cursor()
        cur.execute(f'insert into letters_counterparty (id, name, lft, rght, tree_id, level, prev_org_id, prev_pos_id, type_id, parent_id) values ({r})')
        conn.commit()

