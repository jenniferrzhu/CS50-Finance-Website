# Stock Website

Project for [Week 9](http://cs50.harvard.edu/x/2023/psets/9/finance/) of Harvard's CS50: Introduction to CS

<img width="1414" alt="Screenshot 2023-08-03 at 8 53 38 PM" src="https://github.com/jenniferrzhu/Stock-Website/assets/90798447/7b196e73-1a16-489d-912e-c0dc861ca365">

## Description

New users can register for an account. After logging in, users can access updated ticker information, buy and sell stocks, and see their stock history. The earnings from stocks currently owned is accessible under 'index' which help users decide whether they want to buy or sell the stock using their (fake) money.

## Details

### Register

Create a username and password for a new account. An apology is returned if a field is left empty, a username is taken, or the password and password confirmation don't match.

### Index

This homepage display shows the user's stocks owned, number of shares, original bought price per share, and the current value of each holding. Users can also see their current 'cash' balance and their total balance including stock earnings. 

### Quote

By entering in a company's ticker symbol, users can see the current value of the share. An apology will be returned if the required field is left empty or the entered symbol is invalid.

<img width="243" alt="Screenshot 2023-08-03 at 10 57 54 PM" src="https://github.com/jenniferrzhu/Stock-Website/assets/90798447/5d014e50-09b 4-4c14-85c9-fd8685f0f981">
<img width="151" alt="Screenshot 2023-08-03 at 10 58 01 PM" src="https://github.com/jenniferrzhu/Stock-Website/assets/90798447/75b7be91-8d67-491d-a810-cd457c8be6e8">


### Buy

Users can 'buy' stocks by submitting. a form with the ticker symbol and specified number of shares. If the symbol is valid, the number of shares is a positive interger, and the user can afford the requested purchase, the transaction will be successful, which is indicated by a redirect to the index where the new purchase is recorded in the table. Otherwise, an error will appear. 

### Sell

Users can choose any stock they own and any number of shares to sell. 

### History

All buy and sell transactions are listed in a table summary showing the date and time, action, symbol, shares, and amount. 

---
Please note that the Login and Logout functions and all functions in helpers.py came with the assignment starter code and are not mine. Starter code ©2023 David J. Malan/ Harvard
