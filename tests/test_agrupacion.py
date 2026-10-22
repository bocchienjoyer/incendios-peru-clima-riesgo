"""Casos geográficos pequeños que comprueban el significado de una agrupación."""
import sys
from pathlib import Path
import unittest
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from preparar_detecciones import agrupar


class AgrupacionTest(unittest.TestCase):
    def test_cadena_espacial_y_aislamiento_temporal(self):
        # A-B y B-C están a ~885 m; A-C supera 1 km. D está 60 h después.
        frame=pd.DataFrame({'latitude':[-10,-9.992,-9.984,-10,-10],
            'longitude':[-75,-75,-75,-75,-75.1],
            'fecha_utc':pd.to_datetime(['2026-10-01T00:00Z','2026-10-01T01:00Z',
                '2026-10-01T02:00Z','2026-10-03T12:00Z','2026-10-01T03:00Z'])})
        ids,_=agrupar(frame)
        self.assertEqual(len(set(ids)),3)
        self.assertEqual(ids[0],ids[2])
        self.assertNotEqual(ids[0],ids[3])
        shorter,_=agrupar(frame,distancia_m=500)
        self.assertEqual(len(set(shorter)),5)

    def test_limite_temporal_de_48_horas(self):
        frame=pd.DataFrame({'latitude':[-10,-10], 'longitude':[-75,-75],
            'fecha_utc':pd.to_datetime(['2026-10-01T00:00Z','2026-10-03T00:00Z'])})
        ids,_=agrupar(frame)
        self.assertEqual(ids[0],ids[1])
        frame.loc[1,'fecha_utc']+=pd.Timedelta(seconds=1)
        ids,_=agrupar(frame)
        self.assertNotEqual(ids[0],ids[1])


if __name__=='__main__':
    unittest.main()
