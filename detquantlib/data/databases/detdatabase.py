# Python built-in packages
import warnings
from datetime import datetime
from zoneinfo import ZoneInfo

# Third-party packages
import pandas as pd
import pyodbc
from dateutil.relativedelta import *


class DetDatabase:
    """
    A class to easily interact with the DET database, including fetching and processing data.
    """

    def __init__(
        self,
        username: str,
        password: str,
        server: str,
        database: str,
        connection: pyodbc.Connection = None,
    ):
        """
        Constructor method.

        Args:
            username: Database username
            password: Database password
            server: Database server name
            database: Database name
            connection: Database connection object. This argument does not have to be passed
                when creating the object. It can be set after the object has been created, using
                the open_connection() method.
        """
        self.username = username
        self.password = password
        self.server = server
        self.database = database
        self.connection = connection

        # Define the ODBC driver
        self.driver = "{ODBC Driver 18 for SQL Server}"

    def open_connection(self):
        """Opens a connection to the database."""
        # Create the connection string
        connection_str = (
            f"DRIVER={self.driver};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
            f"UID={self.username};"
            f"PWD={self.password}"
        )
        self.connection = pyodbc.connect(connection_str)

    def close_connection(self):
        """Closes the connection to the database."""
        self.connection.close()

    def query_db(self, query: str) -> pd.DataFrame:
        """
        Short utility method to make an SQL query to the database.

        Args:
            query: SQL query

        Returns:
            Dataframe containing the queried data

        Raises:
            Exception: Raises an error if the SQL query fails
        """
        with warnings.catch_warnings():
            # Pandas UserWarning returned when using pandas with pyodbc. Disable warning
            # temporarily for the SQL query.
            warnings.simplefilter("ignore", category=UserWarning)

            try:
                df = pd.read_sql(query, self.connection)
            except Exception as e:
                # If query fails, close connection before raising the error
                self.close_connection()
                raise

        return df

    def load_entsoe_day_ahead_spot_prices(
        self,
        map_code: str,
        timezone: str,
        start_trading_date: datetime = None,
        end_trading_date: datetime = None,
        start_delivery_date: datetime = None,
        end_delivery_date: datetime = None,
        columns: list = None,
        process_data: bool = True,
    ) -> pd.DataFrame:
        """
        Loads entsoe day-ahead spot prices from the database.

        Args:
            map_code: Map code of the power country/region
            start_trading_date: Start trading date
            end_trading_date: End trading date
                Note: The user should provide either 'start_trading_date' and 'end_trading_date',
                or 'start_delivery_date' and 'end_delivery_date'.
            start_delivery_date: Delivery start date. The start datetime is included in the
                filtering (i.e. delivery dates >= start_date).
            end_delivery_date: Delivery end date. The end datetime is excluded from the filtering
                (i.e. delivery dates < end_date).
                Note: The user should provide either 'start_trading_date' and 'end_trading_date',
                or 'start_delivery_date' and 'end_delivery_date'.
            timezone: Timezone of the power country/region. This argument is important because
                ENTSOE provides all prices in the UTC timezone. We first convert the dates from
                UTC to the local timezone, and then filter for the requested delivery period.
            columns: Requested database table columns. Set columns=["*"] (i.e. as list) to get
                all columns.
            process_data: Indicates if data should be processed convert to standardized format

        Returns:
            Dataframe containing day-ahead spot prices

        Raises:
            ValueError: Raises an error when input arguments 'columns' and 'process_data' are
                not compatible
            ValueError: Raises an error when the combination of trading dates and delivery dates
                is not valid.
        """
        # Input validation
        if process_data and columns is not None:
            raise ValueError(
                "Input argument 'process_data' can only be true if input argument 'columns' "
                "is None."
            )
        if not (
            start_trading_date is not None
            and end_trading_date is not None
            and start_delivery_date is None
            and end_delivery_date is None
        ) and not (
            start_trading_date is None
            and end_trading_date is None
            and start_delivery_date is not None
            and end_delivery_date is not None
        ):
            raise ValueError(
                "Either 'start_trading_date' and 'end_trading_date', or 'start_delivery_date' "
                "and 'end_delivery_date' should be provided."
            )

        # Set default column values
        if columns is None:
            columns = ["DateTime(UTC)", "MapCode", "Price(Currency/MWh)", "Currency"]

        # Always add delivery date column
        if "DateTime(UTC)" not in columns and columns != ["*"]:
            columns.append("DateTime(UTC)")

        # Convert columns from list to string
        if len(columns) == 1:
            columns_str = str(columns[0])
        else:
            columns_str = f"[{'], ['.join(columns)}]"

        # Convert start trading date to start delivery date
        if start_trading_date is not None:
            start_trading_date = pd.Timestamp(start_trading_date).floor("D")
            start_delivery_date = start_trading_date + relativedelta(days=1)

        # Convert start delivery date from local timezone to UTC and string
        start_delivery_date = start_delivery_date.replace(tzinfo=ZoneInfo(timezone))
        start_delivery_date = start_delivery_date.astimezone(ZoneInfo("UTC"))
        start_date_str = start_delivery_date.strftime("%Y-%m-%d %H:%M:%S")

        # Convert end trading date to end delivery date
        if end_trading_date is not None:
            end_trading_date = pd.Timestamp(end_trading_date).floor("D")
            end_delivery_date = end_trading_date + relativedelta(days=2)

        # Convert end date to UTC and string
        end_delivery_date = end_delivery_date.replace(tzinfo=ZoneInfo(timezone))
        end_delivery_date = end_delivery_date.astimezone(ZoneInfo("UTC"))
        end_date_str = end_delivery_date.strftime("%Y-%m-%d %H:%M:%S")

        # Create query
        table = DetDatabaseDefinitions.DEFINITIONS["table_name_entsoe_day_ahead_spot_price"]
        query = (
            f"SELECT {columns_str} FROM {table} "
            f"WHERE MapCode='{map_code}' "
            f"AND [DateTime(UTC)]>='{start_date_str}' "
            f"AND [DateTime(UTC)]<'{end_date_str}' "
        )

        # Query db
        self.open_connection()
        df = self.query_db(query)
        self.close_connection()

        # Sort data by delivery date
        df.sort_values(
            by=["DateTime(UTC)"], axis=0, ascending=True, inplace=True, ignore_index=True
        )

        # Add column with delivery date expressed in local timezone
        datetime_column_name = f"DateTime({timezone})"
        df[datetime_column_name] = df["DateTime(UTC)"].dt.tz_localize("UTC")
        df[datetime_column_name] = df[datetime_column_name].dt.tz_convert(timezone)
        df[datetime_column_name] = df[datetime_column_name].dt.tz_localize(None)

        # Process raw data and convert it to standardized format
        if process_data:
            df = DetDatabase.process_day_ahead_spot_prices(df, timezone)

        return df

    @staticmethod
    def process_day_ahead_spot_prices(df_in: pd.DataFrame, timezone: str) -> pd.DataFrame:
        """
        Processes day-ahead spot prices and converts from ENTSOE format to standardized format.

        Args:
            df_in: Dataframe containing day-ahead spot prices
            timezone: Timezone of the power country/region

        Returns:
            Processed dataframe containing day-ahead spot prices
        """
        map_code_to_commodity_mapper = dict(
            NL={"commodity_name": "DutchPower", "product_code": "Q0B"}
        )

        # Initialize output dataframe
        df_out = pd.DataFrame()

        # Set commodity name
        commodity_name = [
            map_code_to_commodity_mapper[mc]["commodity_name"] for mc in df_in["MapCode"]
        ]
        df_out["CommodityName"] = commodity_name

        # Set product code
        product_code = [
            map_code_to_commodity_mapper[mc]["product_code"] for mc in df_in["MapCode"]
        ]
        df_out["ProductCode"] = product_code

        # Set trading date
        trading_date = [d - relativedelta(days=1, hour=0) for d in df_in[f"DateTime({timezone})"]]
        df_out["TradingDate"] = trading_date

        # Set delivery start date
        df_out["DeliveryStart"] = df_in[f"DateTime({timezone})"].values

        # Set delivery end date
        delivery_end = [d + relativedelta(hours=1) for d in df_in[f"DateTime({timezone})"]]
        df_out["DeliveryEnd"] = delivery_end

        # Set tenor
        df_out["Tenor"] = "Spot"

        # Set price
        df_out["Price"] = df_in["Price(Currency/MWh)"].values

        return df_out

    def load_entsoe_imbalance_prices(
        self,
        map_code: str,
        timezone: str,
        start_trading_date: datetime = None,
        end_trading_date: datetime = None,
        start_delivery_date: datetime = None,
        end_delivery_date: datetime = None,
        columns: list = None,
        process_data: bool = True,
    ) -> pd.DataFrame:
        """
        Loads entsoe imbalance prices from the database.

        Args:
            map_code: Map code of the power country/region
            timezone: Timezone of the power country/region. This argument is important because
                ENTSOE provides all prices in the UTC timezone. We first convert the dates from
                UTC to the local timezone, and then filter for the requested delivery period.
            start_trading_date: Start trading date
            end_trading_date: End trading date
                Note: The user should provide either 'start_trading_date' and 'end_trading_date',
                or 'start_delivery_date' and 'end_delivery_date'.
            start_delivery_date: Delivery start date. The start datetime is included in the
                filtering (i.e. delivery dates >= start_date).
            end_delivery_date: Delivery end date. The end datetime is excluded from the filtering
                (i.e. delivery dates < end_date).
                Note: The user should provide either 'start_trading_date' and 'end_trading_date',
                or 'start_delivery_date' and 'end_delivery_date'.
            columns: Requested database table columns. Set columns=["*"] (i.e. as list) to get
                all columns.
            process_data: Indicates if data should be processed convert to standardized format

        Returns:
            Dataframe containing imbalance prices

        Raises:
            ValueError: Raises an error when input arguments 'columns' and 'process_data' are
                not compatible
            ValueError: Raises an error when the combination of trading dates and delivery dates
                is not valid.
        """
        # Input validation
        if process_data and columns is not None:
            raise ValueError(
                "Input argument 'process_data' can only be true if input argument 'columns' "
                "is None."
            )
        if not (
            start_trading_date is not None
            and end_trading_date is not None
            and start_delivery_date is None
            and end_delivery_date is None
        ) and not (
            start_trading_date is None
            and end_trading_date is None
            and start_delivery_date is not None
            and end_delivery_date is not None
        ):
            raise ValueError(
                "Either 'start_trading_date' and 'end_trading_date', or 'start_delivery_date' "
                "and 'end_delivery_date' should be provided."
            )

        # Set default column values
        if columns is None:
            columns = [
                "DateTime(UTC)",
                "MapCode",
                "PositiveImbalancePrice",
                "NegativeImbalancePrice",
                "Currency",
            ]

        # Always add delivery date column
        if "DateTime(UTC)" not in columns and columns != ["*"]:
            columns.append("DateTime(UTC)")

        # Convert columns from list to string
        if len(columns) == 1:
            columns_str = str(columns[0])
        else:
            columns_str = f"[{'], ['.join(columns)}]"

        # Convert start trading date to start delivery date
        if start_trading_date is not None:
            start_delivery_date = pd.Timestamp(start_trading_date).floor("D")

        # Convert start delivery date from local timezone to UTC and string
        start_delivery_date = start_delivery_date.replace(tzinfo=ZoneInfo(timezone))
        start_delivery_date = start_delivery_date.astimezone(ZoneInfo("UTC"))
        start_date_str = start_delivery_date.strftime("%Y-%m-%d %H:%M:%S")

        # Convert end trading date to end delivery date
        if end_trading_date is not None:
            end_trading_date = pd.Timestamp(end_trading_date).floor("D")
            end_delivery_date = end_trading_date + relativedelta(days=1)

        # Convert end date to UTC and string
        end_delivery_date = end_delivery_date.replace(tzinfo=ZoneInfo(timezone))
        end_delivery_date = end_delivery_date.astimezone(ZoneInfo("UTC"))
        end_date_str = end_delivery_date.strftime("%Y-%m-%d %H:%M:%S")

        # Create query
        table = DetDatabaseDefinitions.DEFINITIONS["table_name_entsoe_imbalance_price"]
        query = (
            f"SELECT {columns_str} FROM {table} "
            f"WHERE MapCode='{map_code}' "
            f"AND [DateTime(UTC)]>='{start_date_str}' "
            f"AND [DateTime(UTC)]<'{end_date_str}' "
        )

        # Query db
        self.open_connection()
        df = self.query_db(query)
        self.close_connection()

        # Sort data by delivery date
        df.sort_values(
            by=["DateTime(UTC)"], axis=0, ascending=True, inplace=True, ignore_index=True
        )

        # Add column with delivery date expressed in local timezone
        datetime_column_name = f"DateTime({timezone})"
        df[datetime_column_name] = df["DateTime(UTC)"].dt.tz_localize("UTC")
        df[datetime_column_name] = df[datetime_column_name].dt.tz_convert(timezone)
        df[datetime_column_name] = df[datetime_column_name].dt.tz_localize(None)

        # Process raw data and convert it to standardized format
        if process_data:
            df = DetDatabase.process_imbalance_prices(df, timezone)

        return df

    @staticmethod
    def process_imbalance_prices(df_in: pd.DataFrame, timezone: str) -> pd.DataFrame:
        """
        Processes imbalance prices and converts from ENTSOE format to standardized format.

        Args:
            df_in: Dataframe containing imbalance prices
            timezone: Timezone of the power country/region

        Returns:
            Processed dataframe containing imbalance prices
        """
        map_code_to_commodity_mapper = dict(
            NL={"commodity_name": "DutchPower", "product_code": "Q0B"}
        )

        # Initialize output dataframe
        df_out = pd.DataFrame()

        # Set commodity name
        commodity_name = [
            map_code_to_commodity_mapper[mc]["commodity_name"] for mc in df_in["MapCode"]
        ]
        df_out["CommodityName"] = commodity_name

        # Set product code
        product_code = [
            map_code_to_commodity_mapper[mc]["product_code"] for mc in df_in["MapCode"]
        ]
        df_out["ProductCode"] = product_code

        # Set trading date
        df_out["TradingDate"] = df_in[f"DateTime({timezone})"].dt.floor("D").values

        # Set delivery start date
        df_out["DeliveryStart"] = df_in[f"DateTime({timezone})"].values

        # Set delivery end date
        delivery_end = [d + relativedelta(minutes=15) for d in df_in[f"DateTime({timezone})"]]
        df_out["DeliveryEnd"] = delivery_end

        # Set tenor
        df_out["Tenor"] = "Imbalance"

        # Set price
        df_out["PositiveImbalancePrice"] = df_in["PositiveImbalancePrice"].values
        df_out["NegativeImbalancePrice"] = df_in["NegativeImbalancePrice"].values

        return df_out

    def load_futures_eod_settlement_prices(
        self,
        commodity_name: str,
        start_trading_date: datetime,
        end_trading_date: datetime,
        tenors: list,
        delivery_type: str,
        columns: list = None,
    ) -> pd.DataFrame:
        """
        Loads futures end-of-day settlement prices from the database, over a user-defined range
        of trading dates.

        Args:
            commodity_name: Commodity name
            start_trading_date: Start trading date
            end_trading_date: End trading date
            tenors: Product tenors (e.g. "Month", "Quarter", "Year")
            delivery_type: Delivery type
            columns: Requested database table columns. Set columns=["*"] (i.e. as list) to get
                all columns.

        Returns:
            Dataframe containing futures end-of-day settlement prices
        """
        # Set default column values
        if columns is None:
            columns = ["*"]

        # Convert columns from list to string
        if len(columns) == 1:
            columns_str = str(columns[0])
        else:
            columns_str = f"[{'], ['.join(columns)}]"

        # Convert tenors from list to string
        tenors_str = f"({' ,'.join([repr(item) for item in tenors])})"

        # Convert dates from datetime to string
        start_trading_date_str = start_trading_date.strftime("%Y-%m-%d")
        end_trading_date_str = end_trading_date.strftime("%Y-%m-%d")

        # Create query
        table = DetDatabaseDefinitions.DEFINITIONS["table_name_futures_eod_settlement_price"]
        query = (
            f"SELECT {columns_str} FROM {table} "
            f"WHERE CommodityName='{commodity_name}' "
            f"AND TradingDate>='{start_trading_date_str}' "
            f"AND TradingDate<='{end_trading_date_str}' "
            f"AND Tenor IN {tenors_str} "
            f"AND DeliveryType='{delivery_type}'"
        )

        # Query db
        self.open_connection()
        df = self.query_db(query)
        self.close_connection()

        # Sort data
        df.sort_values(
            by=["TradingDate", "DeliveryStart", "DeliveryEnd"],
            axis=0,
            ascending=True,
            inplace=True,
            ignore_index=True,
        )

        # Convert dates from datetime.date to pd.Timestamp
        df["TradingDate"] = pd.DatetimeIndex(df["TradingDate"])
        df["DeliveryStart"] = pd.DatetimeIndex(df["DeliveryStart"])
        df["DeliveryEnd"] = pd.DatetimeIndex(df["DeliveryEnd"])

        return df


class DetDatabaseDefinitions:
    """A class containing some hard-coded definitions related to the DET database."""

    DEFINITIONS = dict(
        driver="{ODBC Driver 18 for SQL Server}",
        table_name_entsoe_day_ahead_spot_price="[ENTSOE].[DayAheadSpotPrice]",
        table_name_entsoe_imbalance_price="[ENTSOE].[ImbalancePrice]",
        table_name_futures_eod_settlement_price="[FUT].[EODSettlementPrice]",
    )
