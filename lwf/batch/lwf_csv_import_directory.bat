cd "path\to\project\"
CALL .\<venv name>\Scripts\activate.bat

python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/lebforest.csv -d lwf/data -m leb -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/albforest.csv -d lwf/data -m alb -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/baffield.csv -d lwf/data -m baf -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/babforest.csv -d lwf/data -m bab -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/clbforest.csv -d lwf/data -m clb -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/jubforest.csv -d lwf/data -m jub -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/juffield.csv -d lwf/data -m juf -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/isbforest.csv -d lwf/data -m isb -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/isffield.csv -d lwf/data -m isf -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/btffield.csv -d lwf/data -m btf -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/btbforest.csv -d lwf/data -m btb -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/cibforest.csv -d lwf/data -m cib -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/ciffield.csv -d lwf/data -m cif -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/nabforest.csv -d lwf/data -m nab -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/naffield.csv -d lwf/data -m naf -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/vsbforest.csv -d lwf/data -m vsb -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/vsffield.csv -d lwf/data -m vsf -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/labforest.csv -d lwf/data -m lab -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/laffield.csv -d lwf/data -m laf -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/vobforest.csv -d lwf/data -m vob -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/voffield.csv  -d lwf/data -m vof -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/nebforest.csv  -d lwf/data -m neb -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/neffield.csv  -d lwf/data -m nef -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/nobforest.csv  -d lwf/data -m nob -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/noffield.csv  -d lwf/data -m nof -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/otbforest.csv  -d lwf/data -m otb -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/otffield.csv  -d lwf/data -m otf -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/scbforest.csv  -d lwf/data -m scb -t directory &
python manage.py lwf_csv_import -p LWFMeteo -i lwf/data/scffield.csv  -d lwf/data -m scf -t directory &