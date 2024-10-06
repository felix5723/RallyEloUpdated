from infiniteracing import main as infiniteracing
from reallyrally import main as reallyrally
from raceconsult import main as raceconsult


def main():
    MAX_RALLYS = 10
    infiniteracing(MAX_RALLYS)
    reallyrally(MAX_RALLYS)
    raceconsult(MAX_RALLYS)


main()
