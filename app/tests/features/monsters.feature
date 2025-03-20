Feature: Monster Management and PDF Export
  As a game master
  I want to create, view, edit, and export monster statblocks as PDFs
  So that I can use them in my tabletop RPG campaign

  Scenario: Creating a new monster
    Given a user is logged in
    And they are on the add monster page for a campaign
    When they fill in valid monster information
    Then the monster should be created
    And they should be redirected to the monsters list

  Scenario: Viewing a monster
    Given a user is logged in
    And a monster exists in their campaign
    When they navigate to the monster's view page
    Then they should see all the monster's details

  Scenario: Editing a monster
    Given a user is logged in
    And a monster exists in their campaign
    When they edit the monster with new information
    Then the monster details should be updated
    And they should be redirected to the monster's view page

  Scenario: Deleting a monster
    Given a user is logged in
    And a monster exists in their campaign
    When they delete the monster
    Then the monster should be removed from the database
    And they should be redirected to the monsters list

  Scenario: Exporting a monster as PDF
    Given a user is logged in
    And a monster exists in their campaign
    When they request to export the monster as PDF
    Then a PDF file should be generated
    And the PDF should contain the monster's details 