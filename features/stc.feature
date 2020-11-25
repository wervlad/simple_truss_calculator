Feature: Simple Truss Calculator
    Betty (user) would like to specify and edit trusses, save them to and load from files.

    Scenario: Create truss

        Given console app started

        When I add pinned support

        Then I will see a pinned support on print command

        When I add a beam
        Then I will see a pinned support and a beam on print command
