test_hse

dash_board.py - запуск сервера с дашбордом, требуется 'Введение в историю искусства.csv'

parse_logs.py - парсер логов с двумя опциями problem и video

Примеры запуска:
python .\parse_logs.py --input .\hse_MARK_fall_2017.gz --mode problem --output problems.csv
.\parse_logs.py --input .\hse_MARK_fall_2017.gz --mode video --output video.csv
