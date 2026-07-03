from pathlib import Path

from bin2fits_fast_acquisition_1_3ghz_nodb.bin2fits_fast_acquisition_1_3ghz_app import Bin2FitsFastAcquisition1To3GHzApp

CURRENT_DIR = Path(__file__).resolve().parent
ENV_FILE = CURRENT_DIR.parent.parent.parent.parent / '.env' # этого пути не будет в докере
CONF_TOML_FILE = CURRENT_DIR / 'config' / 'bin2fits_fast_1_3_app.toml'

def main():
    app = Bin2FitsFastAcquisition1To3GHzApp(env_path=ENV_FILE, toml_path=CONF_TOML_FILE)
    app.run()

if __name__ == '__main__':
    main()