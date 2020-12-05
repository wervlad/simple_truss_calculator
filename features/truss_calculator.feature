Feature: Simple Truss Calculator
    Betty (user) would like to calculate trusses.

    @skip
    Scenario: Calculate truss
        When Betty loads truss from examples
        Then autocalculated results are the same as she caclucated manually
