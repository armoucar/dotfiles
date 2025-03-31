import click
from datetime import datetime, timedelta
import locale
import dateutil.relativedelta
from tabulate import tabulate

@click.command()
@click.option("--principal", "-p", type=float, required=True, help="Initial investment amount in BRL")
@click.option("--start-date", "-s", type=click.DateTime(formats=["%Y-%m-%d"]), default=lambda: datetime.now().strftime("%Y-%m-%d"),
              help="Start date (YYYY-MM-DD), defaults to today")
@click.option("--end-date", "-e", type=click.DateTime(formats=["%Y-%m-%d"]), required=True,
              help="End date (YYYY-MM-DD)")
@click.option("--annual-rate", "-r", type=float, default=12.654, help="Annual interest rate (%), defaults to 12.654%")
@click.option("--tax-rate", "-t", type=float, default=17.5, help="Income tax rate (%), defaults to 17.5%")
def simulate(principal, start_date, end_date, annual_rate, tax_rate):
    """
    Simulate a pre-fixed CDB investment with month-by-month breakdown.
    Shows initial amount, monthly accrued interest, final amount, and tax deduction.
    """
    # Convert annual rate to monthly rate
    monthly_rate = (1 + annual_rate/100) ** (1/12) - 1

    # Initialize variables
    current_date = start_date
    current_amount = principal
    original_principal = principal

    # Print header
    click.echo("")
    click.echo(f"Investment Simulation (CDB pre-fixed)")
    click.echo("=" * 50)
    click.echo(f"Principal amount: R$ {principal:,.2f}")
    click.echo(f"Start date: {start_date.strftime('%d %b %Y')}")
    click.echo(f"End date: {end_date.strftime('%d %b %Y')}")
    click.echo(f"Annual interest rate: {annual_rate:.3f}%")
    click.echo(f"Monthly interest rate: {monthly_rate*100:.4f}%")
    click.echo(f"Income tax rate: {tax_rate:.2f}%")
    click.echo("=" * 50)
    click.echo("")

    # Prepare monthly data for tabulation
    headers = ["Month", "Date", "Amount (R$)", "Interest (R$)", "Growth (%)"]
    rows = []

    # Track totals and data for averaging
    total_interest = 0
    total_growth_percent = 0
    monthly_amounts = []
    monthly_interests = []

    # Initial row
    rows.append(["Initial", current_date.strftime("%d %b %Y"), f"{current_amount:,.2f}", "-", "-"])
    monthly_amounts.append(current_amount)

    # Calculate month by month
    month_count = 0
    while current_date < end_date:
        month_count += 1
        # Move to next month
        current_date = current_date + dateutil.relativedelta.relativedelta(months=1)

        # If we've passed the end date, adjust to end date
        if current_date > end_date:
            # Calculate partial month interest based on days
            days_passed = (end_date - (current_date - dateutil.relativedelta.relativedelta(months=1))).days
            days_in_month = (current_date - (current_date - dateutil.relativedelta.relativedelta(months=1))).days
            adjusted_rate = monthly_rate * (days_passed / days_in_month)
            current_date = end_date
            previous_amount = current_amount
            current_amount = current_amount * (1 + adjusted_rate)
            interest_earned = current_amount - previous_amount
        else:
            # Calculate full month interest
            previous_amount = current_amount
            current_amount = current_amount * (1 + monthly_rate)
            interest_earned = current_amount - previous_amount

        # Calculate monthly growth percentage
        monthly_growth_pct = (interest_earned / previous_amount) * 100

        # Add to tracking variables
        total_interest += interest_earned
        total_growth_percent += monthly_growth_pct
        monthly_amounts.append(current_amount)
        monthly_interests.append(interest_earned)

        # Add row to table data
        rows.append([
            month_count,
            current_date.strftime("%d %b %Y"),
            f"{current_amount:,.2f}",
            f"{interest_earned:,.2f}",
            f"{monthly_growth_pct:.4f}%"
        ])

    # Print the monthly breakdown table
    click.echo(tabulate(rows, headers=headers, tablefmt="fancy_grid", numalign="right"))

    # Calculate results
    total_return = current_amount - original_principal
    tax_amount = total_return * (tax_rate / 100)
    net_amount = current_amount - tax_amount

    # Calculate monthly averages
    avg_monthly_amount = sum(monthly_amounts) / len(monthly_amounts)
    avg_monthly_interest = sum(monthly_interests[1:]) / month_count if month_count > 0 else 0
    avg_monthly_growth = total_growth_percent / month_count if month_count > 0 else 0

    # Print summary with monthly averages
    click.echo("\nInvestment Summary:")

    summary_headers = ["Metric", "Value"]
    summary_rows = [
        ["Total period", f"{month_count} months"],
        ["Initial investment", f"R$ {original_principal:,.2f}"],
        ["Gross final amount", f"R$ {current_amount:,.2f}"],
        ["Gross return", f"R$ {total_return:,.2f} ({(total_return/original_principal)*100:.2f}%)"],
        ["Income tax", f"R$ {tax_amount:,.2f} ({tax_rate:.2f}%)"],
        ["Net final amount", f"R$ {net_amount:,.2f}"],
        ["Net return", f"R$ {net_amount - original_principal:,.2f} ({((net_amount - original_principal)/original_principal)*100:.2f}%)"],
        ["", ""],
        ["Monthly Averages", ""],
        ["Avg. account balance", f"R$ {avg_monthly_amount:,.2f}"],
        ["Avg. monthly interest", f"R$ {avg_monthly_interest:,.2f}"],
        ["Avg. monthly growth", f"{avg_monthly_growth:.4f}%"]
    ]

    click.echo(tabulate(summary_rows, headers=summary_headers, tablefmt="simple"))
