Feature: Encounter Management with Monsters
  As a game master
  I want to create encounters with monsters
  So that I can prepare combat scenarios for my tabletop RPG campaign

  Scenario: Creating a new encounter
    Given a user is logged in
    And they are on the add encounter page for a campaign
    When they fill in valid encounter information
    Then the encounter should be created
    And they should be redirected to the encounters list

  Scenario: Adding a monster to an encounter
    Given a user is logged in
    And an encounter exists in their campaign
    When they add a monster to the encounter
    Then the monster should be associated with the encounter
    And they should see the monster in the encounter's monster list

  Scenario: Removing a monster from an encounter
    Given a user is logged in
    And an encounter has a monster
    When they delete the monster from the encounter
    Then the monster should be removed from the encounter
    And they should no longer see the monster in the encounter's monster list

  Scenario: Viewing monsters in an encounter
    Given a user is logged in
    And an encounter has multiple monsters
    When they navigate to the encounter's monsters page
    Then they should see all monsters in the encounter 