import logging
from pathlib import Path
from typing import Any

from gspread_pandas import Client, Spread, conf
from pandas import DataFrame
from pyarabic.trans import convert as transliterate

logger = logging.getLogger(__name__)


class Spreadsheet:
    def __init__(
        self,
        service_account: str,
        sheet_id: str,
        sheet_name: str,
        data_columns: dict[str, str],
        lecture_components: dict[str, str],
    ) -> None:
        self._client: Client = Client(
            config=conf.get_config(
                conf_dir=str(Path(service_account).parent), file_name=service_account
            )
        )
        self.worksheet: Spread = Spread(sheet_id, sheet=sheet_name, client=self._client)
        self.df: DataFrame = self.worksheet.sheet_to_df().iloc[1:]
        # Add slug columns
        for column_id in data_columns:
            self.df[f"{column_id}_slug"] = self.df[column_id].apply(
                lambda x: "_".join(
                    transliterate(str(x), "arabic", "tim").lower().replace("\\", "").split(" ")
                )
            )
        # Add id column
        self.df["id"] = self.df.apply(
            lambda row: "_".join(
                [row[f"{col_id}_slug"] for col_id in data_columns] + [row["lecture"]]
            ),
            axis=1,
        )
        self.hierarchy = self.create_hierarchy(data_columns, lecture_components)

    def create_hierarchy(
        self, data_columns: dict[str, str], lecture_components: dict[str, str]
    ) -> dict[str, Any]:
        hierarchy: dict[str, Any] = {}
        for data_column_id, data_column_name in data_columns.items():
            hierarchy[data_column_name] = {}
            data: DataFrame
            for group_key, data in self.df.groupby(
                [data_column_id] if data_column_id == "series" else [data_column_id, "series"],
                sort=False,
                dropna=True,
            ):
                current_level = hierarchy[data_column_name]
                levels = group_key if isinstance(group_key, tuple) else (group_key,)
                for level in levels:
                    level_name = str(level).strip()
                    if level_name not in current_level:
                        current_level[level_name] = {}
                    current_level = current_level[level_name]
                for index, row in enumerate(data.to_dict("records"), start=1):
                    current_level[str(row.get("lecture") or index)] = {
                        component: row.get(component) for component in lecture_components
                    } | {"__data": True, "id": row.get("id")}
        return hierarchy

    def navigate_hierarchy(self, path: list[str]) -> dict | None:
        current_level = self.hierarchy
        for item in path:
            if item in current_level:
                current_level = current_level[item]
            else:
                return None
        return current_level
