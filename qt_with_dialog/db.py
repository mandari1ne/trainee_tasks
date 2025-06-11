import sqlite3 as sql


class DB:
    def __init__(self, db: str):
        self.db = db
        self.connection = sql.connect(self.db)

    def get_name_of_tables(self):
        with self.connection:
            cur = self.connection.execute('''
                SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ''')

            self.tables = [row[0] for row in cur.fetchall()]

            return self.tables

    def get_table_columns(self, table_name):
        with self.connection:
            cur = self.connection.execute(f"Pragma table_info ({table_name})")
            column_info = cur.fetchall()

            return column_info

    def get_table_fk(self, table_name):
        with self.connection:
            cur = self.connection.execute(f"Pragma foreign_key_list ({table_name})")

            fks = cur.fetchall()

            # fk: {имя_столбца: (таблица, столбец)}
            return {fk[3]: (fk[2], fk[4]) for fk in fks}

    def get_related_value(self, fk_table, fk_col, fk_value):
        with self.connection:
            try:
                row = self.connection.execute(
                    f'SELECT * FROM {fk_table} WHERE {fk_col} = ?',
                    (fk_value,)
                ).fetchone()

                return row[1] if row else ""
            except sql.Error as e:
                print(f"Ошибка получения связанного значения: {e}")
                return ""

    def get_table_data(self, table_name):
        with self.connection:
            cur = self.connection.execute(f'''
                SELECT * FROM {table_name}
            ''')

            data = cur.fetchall()

            column_info = self.get_table_columns(table_name)
            column_names = [col[1] for col in column_info]

            fk_info = self.get_table_fk(table_name)

            processed_data = []
            for row in data:
                new_row = list(row)
                for col_idx, col_name in enumerate(column_names):
                    if col_name in fk_info:
                        fk_table, fk_col = fk_info[col_name]
                        fk_value = row[col_idx]

                        related_value = self.get_related_value(fk_table, fk_col, fk_value)

                        new_row[col_idx] = f"{fk_value}-{related_value}" if fk_value is not None else ""

                processed_data.append(tuple(new_row))

            return processed_data

    def delete_row(self, table_name, row_id):
        with self.connection:
            self.connection.execute(f'''
                   DELETE FROM {table_name} WHERE id = ?
               ''', (row_id,))

            self.connection.commit()

    def insert_data(self, table_name, values):
        with self.connection:
            columns = ', '.join(values.keys())
            insert_value = ', '.join(['?'] * len(values))

            self.connection.execute(f'''
                INSERT INTO {table_name} ({columns}) VALUES ({insert_value})
            ''', tuple(values.values()))

            self.connection.commit()

    def update_row(self, table_name, row_id, values):
        with self.connection:
            update_value = ', '.join(f'{col} = ?' for col in values.keys())
            params = list(values.values()) + [row_id]

            self.connection.execute(f'''
                   UPDATE {table_name} SET {update_value} WHERE id = ?
               ''', params)

            self.connection.commit()
