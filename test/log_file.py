from pathlib import Path

from end4train.binary_parser import get_records_from_log_file, record_objects_to_list_of_series, parse_log, \
    get_process_data_from_records, get_data_from_process_data


def test_log_file_load():
    file = Path("data") / "20240318" / "eot.dat"
    records = get_records_from_log_file(file.read_bytes())
    process_data = get_process_data_from_records(records)
    dataframe = get_data_from_process_data(process_data)

    # dataframe.to_parquet(file.with_suffix(".parquet"))

    s = record_objects_to_list_of_series(records)
    pass


if __name__ == "__main__":
    test_log_file_load()