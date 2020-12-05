Feature: Truss Builder
    Betty (user) would like to specify and edit trusses, save them to and load from files.

    Scenario: Add elements to newly created truss
        Given new truss created
        When Betty adds pinned support
        Then she will see a pinned support in the truss

        Given new truss created
        When Betty adds pinned support
            And then adds a beam
        Then she will see a pinned support and a beam in the truss

    Scenario: Edit truss
        Given new truss created
        When Betty adds pinned support
            And then deletes pinned support
        Then the truss is empty

    Scenario: Save & load truss
        Given some elements added to new truss
        When Betty saves truss to file 'truss.json'
        Then she can load exactly the same truss from file 'truss.json'
