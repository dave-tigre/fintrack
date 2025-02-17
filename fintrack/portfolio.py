# A class to function as a portfolio of stocks is defined in the snippet below. The class has the following methods:
# Add a stock to the portfolio: add_stock(symbol, shares, price)
# Remove a stock from the portfolio: remove_stock(symbol, shares)
# Get the value of a stock in the portfolio: get_stock_value(symbol)
# Get the total value of the portfolio: get_total_value()
# The class is defined as follows:

import pandas as pd
from datetime import datetime
import pickle
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / 'data'
print(DATA_DIR)
class Portfolio:
    def __init__(self, filename=None, load_pickle = False, load_file=False):
        self.transactions = pd.DataFrame(columns=['Symbol', 'Action', 'Shares', 'Price'])
        self.positions = pd.DataFrame(columns=['Symbol', 'Shares', 'Cost Basis', 'Market Value'])
        self.cash = 0
        
        if load_file and load_pickle:
            raise ValueError("Only one of load_file and load_pickle can be True")
        
        if load_file:
            self.load_csv(filename)
            
        if load_pickle:
            self.load_pickle(filename)
            
    def save_pickle(self, filename):
        """
        Saves the portfolio to a binary file.

        Args:
            filename (str): The name of the file to save the portfolio to.
        """
        with open(filename, 'wb') as f:
            pickle.dump(self, f)
            
    def load_pickle(self, filename):
        """
        Reads the portfolio from a binary file.

        Args:
            filename (str): The name of the file to read the portfolio from.
        """
        with open(filename, 'rb') as f:
            portfolio = pickle.load(f)
            self.transactions = portfolio.transactions
            self.positions = portfolio.positions
            self.cash = portfolio.cash
            
    def save_csv(self, filename):
        """
        Saves the portfolio to a CSV file.

        Args:
            filename (str): The name of the file to save the portfolio to.
        """
        self.transactions.to_csv(filename + '_transactions.csv')
        self.positions.to_csv(filename + '_positions.csv')
        with open(filename + '_cash.txt', 'w') as f:
            f.write(str(self.cash))
            
    def load_csv(self, filename): 
        """
        Reads the portfolio from a CSV file.

        Args:
            filename (str): The name of the file to read the portfolio from.
        """
        self.transactions = pd.read_csv(filename + '_transactions.csv', index_col=0)
        self.positions = pd.read_csv(filename + '_positions.csv', index_col=0)
        with open(filename + '_cash.txt', 'r') as f:
            self.cash = float(f.read())
        
    def deposit(self, amount):
        """
        Deposits an amount into the portfolio.

        Args:
            amount (float): The amount to deposit.
        """
        self.cash += amount
        
    def withdraw(self, amount):
        """
        Withdraws an amount from the portfolio.

        Args:
            amount (float): The amount to withdraw.
        """
        if amount > self.cash:
            raise ValueError("Insufficient funds to withdraw")
        self.cash -= amount
        
        
    def  record_transaction(self, date, symbol, action, shares, price):
        """
        Records a new transaction to the portfolio.

        Args:
            date (str): Transaction date.
            symbol (str): Stock symbol.
            action (str): 'Buy' or 'Sell'.
            shares (int): Number of shares.
            price (float): Price per share.
        """
        new_transaction = pd.DataFrame(data = {
                                        'Symbol': [symbol],
                                        'Action': [action],
                                        'Shares': [shares],
                                        'Price': [price]},
                                       index = [date])
        
        if self.transactions.empty:
            self.transactions = new_transaction
            
        self.transactions = pd.concat([self.transactions, new_transaction])
        self.__update_positions(symbol, action, shares, price)

    def __update_positions(self, symbol, action, shares, price):
        """
        Updates the portfolio positions based on the transaction.

        Args:
            date (str): Transaction date.
            symbol (str): Stock symbol.
            action (str): 'Buy' or 'Sell'.
            shares (int): Number of shares.
            price (float): Price per share.
        """
        if action == 'Buy':
            cost_basis = shares * price
            self.cash -= cost_basis
            if cost_basis > self.cash:
                raise ValueError("Insufficient funds to purchase stock")
            # Add new position or increase existing position
            if symbol not in self.positions.index:
                self.positions.loc[symbol] = [symbol, shares, shares * price, shares * price]
            else:
                self.positions.loc[symbol, 'Shares'] += shares
                self.positions.loc[symbol, 'Cost Basis'] += cost_basis
                self.positions.loc[symbol, 'Market Value'] = self.positions.loc[symbol, 'Shares'] * price
        elif action == 'Sell':
            # Decrease or remove existing position
            if symbol in self.positions.index:
                if shares > self.positions.loc[symbol, 'Shares']:
                    raise ValueError("Insufficient shares to sell")
                self.positions.loc[symbol, 'Shares'] -= shares
                self.positions.loc[symbol, 'Cost Basis'] -= shares * price
                self.cash += shares * price
                self.positions.loc[symbol, 'Market Value'] = self.positions.loc[symbol, 'Shares'] * price
                if self.positions.loc[symbol, 'Shares'] == 0:
                    self.positions = self.positions.drop(symbol)

    def value(self, current_prices=None):
        """
        Calculates the current portfolio value.

        Args:
            current_prices (dict): A dictionary of current stock prices.

        Returns:
            float: The current portfolio value.
        """
        if current_prices:
            self.positions['Current Price'] = self.positions.index.map(current_prices)
            self.positions['Market Value'] = self.positions['Shares'] * self.positions['Current Price']
        return self.positions['Market Value'].sum() + self.cash

    def calculate_return(self, initial_investment):
        """
        Calculates the portfolio's return.

        Args:
            initial_investment (float): The initial investment amount.

        Returns:
            float: The portfolio's return.
        """
        
        current_value = self.value()
        return (current_value - initial_investment) / initial_investment


if __name__ == "__main__":
    # Example usage:
    portfolio = Portfolio()
    initial_investment = 25000
    portfolio.deposit(initial_investment)
    
    print("Portfolio Cash:", portfolio.cash)

    # Record transactions
    portfolio.record_transaction(datetime(2023,11,21), 'AAPL', 'Buy', 10, 150)
    portfolio.record_transaction(datetime(2023,12,15), 'GOOGL', 'Buy', 5, 2000)
    print("Portfolio Cash:", portfolio.cash)
    portfolio.record_transaction(datetime(2024, 1,10), 'AAPL', 'Sell', 5, 170)
    print("Portfolio Cash:", portfolio.cash)

    print("Transactions")
    print(portfolio.transactions.head())
    print("Positions")
    print(portfolio.positions.head())

    # Calculate portfolio value
    current_prices = {'AAPL': 160, 'GOOGL': 2100}
    portfolio_value = portfolio.value(current_prices)
    print("Portfolio Value:",portfolio_value)

    # Calculate portfolio return
    portfolio_return = portfolio.calculate_return(initial_investment)
    print("Portfolio Return:",portfolio_return * 100, "%")
    
    # Save portfolio to file
    portfolio.save_pickle(f'{DATA_DIR}/portfolio.pkl')
    
    # Save portfolio to CSV
    portfolio.save_csv(f'{DATA_DIR}/portfolio.csv')
    
    # Read portfolio from file
    new_portfolio = Portfolio(f'{DATA_DIR}/portfolio.pkl', load_pickle=True)
    
    print("New Portfolio Cash:", new_portfolio.cash)
    print("New Portfolio Transactions")
    print(new_portfolio.transactions.head())
    print("New Portfolio Positions")
    print(new_portfolio.positions.head())
    print("New Portfolio Value:", new_portfolio.value(current_prices))
    print("New Portfolio Return:", new_portfolio.calculate_return(initial_investment) * 100, "%")
    
    # Read portfolio from CSV
    csv_portfolio = Portfolio(f'{DATA_DIR}/portfolio.csv', load_file=True)
    
    print("CSV Portfolio Cash:", csv_portfolio.cash)
    print("CSV Portfolio Transactions")
    print(csv_portfolio.transactions.head())
    print("CSV Portfolio Positions")
    print(csv_portfolio.positions.head())
    print("CSV Portfolio Value:", csv_portfolio.value(current_prices))
    print("CSV Portfolio Return:", csv_portfolio.calculate_return(initial_investment) * 100, "%")
    