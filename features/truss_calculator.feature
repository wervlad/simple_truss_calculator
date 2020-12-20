Feature: Simple Truss Calculator
    Betty (user) would like to calculate trusses.

    Scenario: Calculate trusses
        When Betty loads truss from 'examples/truss01.json'
        Then results for 1st truss are the same as she caclucated manually

        When Betty loads truss from 'examples/truss02.json'
        Then calculate raises exception 'truss is statically indeterminate'

        When Betty loads truss from 'examples/truss03.json'
        Then calculate raises exception 'unbalanced truss'

        When Betty loads truss from 'examples/truss04.json'
        Then results for 4th truss are the same as she caclucated manually

        When Betty loads truss from 'examples/truss05.json'
        Then results for 5th truss are the same as she caclucated manually

        When Betty loads truss from 'examples/truss06.json'
        Then results for 6th truss are the same as she caclucated manually

        When Betty loads truss from 'examples/truss07.json'
        Then results for 7th truss are the same as she caclucated manually

        When Betty loads truss from 'examples/truss08.json'
        Then results for 8th truss are the same as she caclucated manually
