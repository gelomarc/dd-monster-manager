Feature: User Authentication
  As a user
  I want to be able to register, login, and logout
  So that I can access and manage my campaigns

  Scenario: User registration
    Given the user is on the registration page
    When they fill in valid registration information
    Then they should be redirected to the login page

  Scenario: User login
    Given a registered user
    And the user is on the login page
    When they fill in valid login credentials
    Then they should be redirected to the campaigns page

  Scenario: User logout
    Given a registered user
    And the user is logged in
    When they click on the logout button
    Then they should be redirected to the index page 