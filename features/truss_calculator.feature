Feature: Simple Truss Calculator
    Betty (user) would like to calculate trusses.

    Scenario: Calculate truss
        When Betty loads truss from 'examples/truss01.json'
        Then autocalculated results are the same as she caclucated manually
