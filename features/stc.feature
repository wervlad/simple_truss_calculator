Feature: Simple Truss Calculator
    Betty (user) would like to specify and edit trusses, save them to and load from files.

    Scenario: Create truss
        Given new truss created
        When Betty adds pinned support
        Then Betty will see a pinned support on print command

        Given new truss created
        When Betty adds pinned support
            And Betty adds a beam
        Then Betty will see a pinned support and a beam on print command

        Given new truss created
        When Betty misstypes and tries to add a ream
        Then Betty will see nothing on print command
