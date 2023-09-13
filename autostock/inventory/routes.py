from flask import Blueprint, render_template, flash, url_for, redirect
from flask_login import login_required, current_user
from autostock import db
from autostock.models import InventoryItem, Supplier
from autostock.inventory.forms import AddInventory


inventory = Blueprint('inventory', __name__)



@inventory.route('/inventory/view', methods=['GET', 'POST'])
@login_required
def view_inventories():
    inventories = InventoryItem.query.all()
    return render_template('view_inventories.html', title='Inventories', inventories=inventories)


@inventory.route('/inventory/add', methods=['GET', 'POST'])
@login_required
def add_inventory():
    if not current_user.is_authenticated or not current_user.is_superuser:
        flash('You are not authorized to access this page.', 'danger')
        return redirect(url_for('mechanic_dashboard'))
    form = AddInventory()

    # Query the database and generate choices within the view function
    suppliers = Supplier.query.all()
    form.supplier.choices = [(str(s.id), s.name) for s in suppliers]

    if current_user.is_superuser:
        if form.validate_on_submit():
            try:
                inventory = InventoryItem(
                name=form.name.data,
                quantity=form.quantity.data,
                category=form.category.data,
                supplier=Supplier.query.get(int(form.supplier.data))  # Retrieve the selected supplier
                )
                db.session.add(inventory)
                db.session.commit()
                flash('The inventory items have been inserted!', 'success')
                return redirect(url_for('owner_dashboard'))
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while adding inventory items.', 'error')
                print(str(e))
    return render_template('add_inventory.html', title='Add Inventory', legend='Add Inventory', form=form)



@inventory.route('/inventory/low_inventory', methods=['GET', 'POST'])
@login_required
def low_inventory():
    low_inventory = InventoryItem.query.filter(InventoryItem.quantity <= InventoryItem.low_stock_threshold)
    return render_template('low_inventory.html', title='Low Inventory', low_inventory=low_inventory)


@inventory.route('/inventory/finished_inventory', methods=['GET', 'POST'])
@login_required
def finished_inventory():
    finished_inventory = InventoryItem.query.filter(InventoryItem.quantity == 0)
    return render_template('finished_inventory.html', title='Finished Inventory', finished_inventory=finished_inventory)



