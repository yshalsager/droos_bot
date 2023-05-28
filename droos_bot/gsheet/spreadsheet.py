import logging
from pathlib import Path

from gspread_pandas import Client, Spread, conf
from pandas import DataFrame

logger = logging.getLogger(__name__)


class Spreadsheet:
    def __init__(
        self,
        service_account: str,
        sheet_id: str,
        sheet_name: str,
        data_columns: dict[str, str],
    ) -> None:
        self._client: Client = Client(
            config=conf.get_config(
                conf_dir=str(Path(service_account).parent), file_name=service_account
            )
        )
        self.worksheet: Spread = Spread(sheet_id, sheet=sheet_name, client=self._client)
        # self.table_headers: list[str] = self._sheet.sheet.row_values(1)
        # self.items: list[Dict[str, str]] = self._sheet.sheet.get_all_records()[1:]
        # self.df = self.worksheet.sheet_to_df()
        self.df: DataFrame = self.worksheet.sheet_to_df().iloc[1:]
        # self.series = self.df.series.unique().tolist()
        # self.series: Series = self.df.groupby("slug")["series"].unique()
        self.data_columns = []
        for data_column_id, _ in data_columns.items():
            self.data_columns.append(data_column_id)
            setattr(
                self,
                data_column_id,
                self.df.groupby(f"{data_column_id}_slug")[data_column_id].unique(),
            )

    #
    # def __len__(self):
    #     return len(self.items)
