Feature: Campaign Management
  As a user
  I want to be able to view, create, and delete campaigns
  So that I can manage my campaigns effectively

  Scenario: View empty campaign list
    Given the user is logged in
    When they visit the campaigns page
    Then they should see an empty campaign list

  Scenario: Create a new campaign
    Given the user is logged in
    When they go to the create campaign page
    And they create a new campaign with valid information
    Then they should see the campaign in the campaign list

  Scenario: Delete an existing campaign
    Given the user is logged in
    And the user has created a campaign
    When they delete the campaign
    Then the campaign should be removed from the list 