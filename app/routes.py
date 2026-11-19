from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    session,
    flash
)

from . import db
from .models import (
    Conversation,
    Message,
    CampusItem,
    Admin,
    Feedback
)

from .assistant import answer, classify


bp = Blueprint('main', __name__)


@bp.get('/')
def index():
    conversations = Conversation.query.order_by(
        Conversation.created_at.desc()
    ).all()

    return render_template(
        'index.html',
        conversations=conversations
    )


@bp.get('/chat/<int:conversation_id>')
def chat(conversation_id):
    conv = Conversation.query.get_or_404(conversation_id)

    conversations = Conversation.query.order_by(
        Conversation.created_at.desc()
    ).all()

    return render_template(
        'chat.html',
        conversation=conv,
        conversations=conversations
    )


@bp.post('/chat')
def create_chat():

    query = request.form.get('message', '').strip()

    if not query:
        return redirect(url_for('main.index'))

    conv = Conversation(
        title=query[:55],
        category=classify(query)
    )

    db.session.add(conv)
    db.session.flush()

    db.session.add(
        Message(
            conversation_id=conv.id,
            role='user',
            content=query
        )
    )

    reply, category, sources = answer(query, [])

    conv.category = category

    db.session.add(
        Message(
            conversation_id=conv.id,
            role='assistant',
            content=reply,
            source=sources[0].source if sources else None
        )
    )

    db.session.commit()

    return redirect(
        url_for(
            'main.chat',
            conversation_id=conv.id
        )
    )


@bp.post('/chat/<int:conversation_id>/message')
def send_message(conversation_id):

    conv = Conversation.query.get_or_404(conversation_id)

    query = request.form.get('message', '').strip()

    if not query:
        return redirect(
            url_for(
                'main.chat',
                conversation_id=conv.id
            )
        )

    history = [
        {
            'role': m.role,
            'content': m.content
        }
        for m in conv.messages
    ]

    db.session.add(
        Message(
            conversation_id=conv.id,
            role='user',
            content=query
        )
    )

    reply, category, sources = answer(
        query,
        history
    )

    conv.category = category

    if conv.title == 'New conversation' or len(conv.messages) <= 2:
        conv.title = query[:55]

    db.session.add(
        Message(
            conversation_id=conv.id,
            role='assistant',
            content=reply,
            source=sources[0].source if sources else None
        )
    )

    db.session.commit()

    return redirect(
        url_for(
            'main.chat',
            conversation_id=conv.id
        )
    )


@bp.post('/chat/<int:conversation_id>/delete')
def delete_chat(conversation_id):

    conv = Conversation.query.get_or_404(
        conversation_id
    )

    db.session.delete(conv)
    db.session.commit()

    return redirect(url_for('main.index'))


@bp.post('/api/feedback')
def submit_feedback():

    message_id = request.form.get('message_id')
    rating = request.form.get('rating')

    if rating not in ['helpful', 'not_helpful']:
        return jsonify({
            'success': False,
            'error': 'Invalid rating'
        }), 400

    message = Message.query.get_or_404(message_id)

    if message.role != 'assistant':
        return jsonify({
            'success': False,
            'error': 'Feedback can only be submitted for assistant messages'
        }), 400

    existing = Feedback.query.filter_by(
        message_id=message.id
    ).first()

    if existing:
        existing.rating = rating
    else:
        db.session.add(
            Feedback(
                message_id=message.id,
                rating=rating
            )
        )

    db.session.commit()

    return jsonify({
        'success': True,
        'rating': rating
    })


@bp.get('/api/feedback/stats')
def feedback_stats():

    helpful = Feedback.query.filter_by(
        rating='helpful'
    ).count()

    not_helpful = Feedback.query.filter_by(
        rating='not_helpful'
    ).count()

    total = helpful + not_helpful

    satisfaction = (
        round(helpful / total * 100, 1)
        if total
        else 0
    )

    return jsonify({
        'total': total,
        'helpful': helpful,
        'not_helpful': not_helpful,
        'satisfaction': satisfaction
    })


@bp.get('/api/health')
def health():

    return jsonify({
        'status': 'online',
        'service': 'AI Campus Assistant'
    })


@bp.get('/api/stats')
def stats():

    return jsonify({
        'conversations': Conversation.query.count(),
        'messages': Message.query.count(),
        'campus_items': CampusItem.query.count(),
        'feedback': Feedback.query.count(),
        'categories': {
            category: CampusItem.query.filter_by(
                category=category
            ).count()
            for category in [
                'academics',
                'faculty',
                'campus',
                'events',
                'notices',
                'services'
            ]
        }
    })


@bp.get('/api/conversation/<int:conversation_id>')
def conversation_api(conversation_id):

    conversation = Conversation.query.get_or_404(
        conversation_id
    )

    return jsonify({
        'id': conversation.id,
        'title': conversation.title,
        'category': conversation.category,
        'messages': [
            {
                'id': message.id,
                'role': message.role,
                'content': message.content,
                'source': message.source,
                'created_at': message.created_at.isoformat(),
                'feedback': (
                    message.feedback.rating
                    if message.feedback
                    else None
                )
            }
            for message in conversation.messages
        ]
    })


@bp.get('/admin')
def admin():

    if not session.get('admin'):
        return redirect(
            url_for('main.admin_login')
        )

    items = CampusItem.query.order_by(
        CampusItem.category,
        CampusItem.title
    ).all()

    feedback_total = Feedback.query.count()

    helpful = Feedback.query.filter_by(
        rating='helpful'
    ).count()

    not_helpful = Feedback.query.filter_by(
        rating='not_helpful'
    ).count()

    return render_template(
        'admin.html',
        items=items,
        feedback_total=feedback_total,
        helpful=helpful,
        not_helpful=not_helpful
    )


@bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':

        user = request.form.get('username')
        pw = request.form.get('password')

        admin = Admin.query.filter_by(
            username=user,
            password=pw
        ).first()

        if admin:

            session['admin'] = True

            return redirect(
                url_for('main.admin')
            )

        flash('Invalid login')

    return render_template('login.html')


@bp.post('/admin/logout')
def admin_logout():

    session.pop('admin', None)

    return redirect(url_for('main.index'))


@bp.post('/admin/item')
def add_item():

    if not session.get('admin'):
        return redirect(
            url_for('main.admin_login')
        )

    item = CampusItem(
        category=request.form['category'],
        title=request.form['title'],
        content=request.form['content'],
        source=request.form.get(
            'source',
            'Campus database'
        )
    )

    db.session.add(item)
    db.session.commit()

    return redirect(url_for('main.admin'))


@bp.post('/admin/item/<int:item_id>/delete')
def delete_item(item_id):

    if not session.get('admin'):
        return redirect(
            url_for('main.admin_login')
        )

    item = CampusItem.query.get_or_404(item_id)

    db.session.delete(item)
    db.session.commit()

    return redirect(url_for('main.admin'))