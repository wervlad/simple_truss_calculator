Feature: Simple Truss Calculator
    Betty (user) would like to calculate trusses.

    Scenario: Calculate trusses
        When Betty loads truss from 'examples/truss01.json'
        Then autocalculated results are the same as she caclucated manually

        When Betty loads truss from 'examples/truss02.json'
        Then calculate raises exception 'truss is statically indeterminate'
