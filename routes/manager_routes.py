"""
Manager routes - Admin dashboard for viewing orders
"""
import logging
from flask import Blueprint, render_template, request
from services import OrderProcessor

logger = logging.getLogger(__name__)

manager_bp = Blueprint('manager', __name__, url_prefix='/manager')


@manager_bp.route('/orders')
def orders():
    """Display all orders for the manager"""
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get orders and total count
        all_orders = OrderProcessor.get_all_orders(limit=per_page, offset=offset)
        total_orders = OrderProcessor.get_order_count()
        
        # Calculate pagination info
        total_pages = (total_orders + per_page - 1) // per_page  # Ceiling division
        has_prev = page > 1
        has_next = page < total_pages
        
        return render_template(
            'manager/orders.html',
            orders=all_orders,
            page=page,
            per_page=per_page,
            total_orders=total_orders,
            total_pages=total_pages,
            has_prev=has_prev,
            has_next=has_next
        )
    except Exception as e:
        logger.error(f"Error loading manager orders page: {str(e)}")
        return render_template('500.html'), 500


@manager_bp.route('/orders/<int:order_id>')
def order_detail(order_id):
    """Display detailed view of a specific order"""
    try:
        order = OrderProcessor.get_order_by_id(order_id)
        
        if order is None:
            logger.warning(f"Manager accessed non-existent order ID: {order_id}")
            return render_template('404.html'), 404
        
        return render_template('manager/order_detail.html', order=order)
    except Exception as e:
        logger.error(f"Error loading order detail for order {order_id}: {str(e)}")
        return render_template('500.html'), 500
