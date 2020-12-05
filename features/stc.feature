Feature: Simple Truss Calculator
    Betty (user) would like to specify and edit trusses, save them to and load from files.

    Scenario: Add elements to newly created truss
        Given new truss created
        When Betty adds pinned support
        Then she will see a pinned support on print command

        Given new truss created
        When Betty adds pinned support
            And then adds a beam
        Then she will see a pinned support and a beam on print command

        Given new truss created
        When Betty misstypes and tries to add a Ream
        Then she will see nothing on print command

    Scenario: Edit truss
        Given new truss created
        When Betty adds pinned support
            And then deletes pinned support
        Then she will see nothing on print command

    Scenario: Save & load truss
        Given some elements added to new truss
        When Betty saves truss to file 'truss.json'
        Then she can load exactly the same truss from file 'truss.json'

    @skip
    Scenario: Calculate truss
        When Betty loads truss from examples
        Then autocalculated results are the same as she caclucated manually
