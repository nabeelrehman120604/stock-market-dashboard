import sqlite3
import pandas as pd


class StockDatabase:
    def __init__(self, db_path: str = "stocks.db") -> None:
        self.db_path = db_path
        self._create_table()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _create_table(self) -> None:
        query = """
        CREATE TABLE IF NOT EXISTS stock_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            UNIQUE(symbol, date)
        );
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            conn.commit()

    def stock_exists(self, symbol: str) -> bool:
        query = "SELECT 1 FROM stock_prices WHERE symbol = ? LIMIT 1;"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (symbol,))
            result = cursor.fetchone()
            return result is not None

    def insert_stock_data(self, df: pd.DataFrame, symbol: str) -> None:
        if df.empty:
            return

        df = df.copy()
        df.reset_index(inplace=True)

        df.rename(columns=str.title, inplace=True)
        df["symbol"] = symbol
        df["date"] = df["Date"].dt.strftime("%Y-%m-%d")

        records = df[["symbol", "date", "Open", "High", "Low", "Close", "Volume"]].values.tolist()

        query = """INSERT OR IGNORE INTO stock_prices 
        (symbol, date, open, high, low, close, volume) 
        VALUES (?, ?, ?, ?, ?, ?, ?);
                """

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, records)
            conn.commit()

    def get_stock_data(self, symbol: str) -> pd.DataFrame:
        query = """SELECT date, open, high, low, close, volume 
                   FROM stock_prices 
                   WHERE symbol = ? ORDER BY date ASC;
        """

        with self._get_connection() as conn:
            df = pd.read_sql_query(query, conn, params=(symbol,))

        if not df.empty:
            df["date"] = pd.to_datetime(df["date"])
            df.set_index("date", inplace=True)

        return df