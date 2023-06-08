from ..models.db import db
from ..models.song import Song
from ..models.images import SongImage
from ..models.comment import Comment
from ..models.likes import SongLike
from ..models.user import User
from ..forms.song_form import SongForm, EditSongForm
from ..forms.comment_form import CommentForm

from flask import Blueprint, redirect, url_for, render_template, jsonify, request
from flask_login import login_required, current_user, logout_user

songs_routes = Blueprint('songs', __name__)

# view all songs
@songs_routes.route('/', methods=['GET'])
def get_all_songs():
    songs = Song.query.all()
    return {
        "Songs": [song.to_dict() for song in songs]
    }

#view song by song id
@songs_routes.route('/<int:id>', methods=['GET'])
def song_detail(id):
    # Retrieve the song details from the database
    song = Song.query.get(id)
    # Check if the song exists in the database
    if(song):
    # Print the song details
        image = SongImage.query.get(id)
        likes = SongLike.query.get(id)
        comments = Comment.query.get(id)

        res = {
            "songId": song.id,
            "userId": song.user_id,
            "name": song.name,
            "artists": song.artists,
            "genre": song.genre,
            "description": song.description,
            "SongImage": image.img_url,
            "SongLikesCnt": likes.id,
            "SongComments": comments.comment
        }

        return jsonify(res), 200

    else:

        res = {
            "message": "Song could not be found.",
            "statusCode": 404
        }

        return jsonify(res), 404

#create new song
@songs_routes.route('/new', methods=['POST'])
@login_required
def create_song():
    form = SongForm()
    form['csrf_token'].data = request.cookies['csrf_token']
    if form.validate_on_submit():
        name = form.name.data
        artists = form.artists.data
        genre = form.genre.data
        description = form.description.data
        audio_url = form.audio_url.data

        song = Song(
            user_id=current_user.id,
            name=name,
            artists=artists,
            genre=genre,
            description=description,
            audio_url=audio_url
        )

        db.session.add(song)
        db.session.commit()

        return jsonify(song.to_dict()), 201
    else:
        return jsonify(form.errors), 400

#update a song
@songs_routes.route('/<int:id>', methods=['PUT'])
@login_required
def update_song(id):
    song = Song.query.get(id)
    if song and current_user.id == song.user_id:
        """

        all this code is to update the song in the database, but also theory

            """
        form = EditSongForm()
        form['csrf_token'].data = request.cookies['csrf_token']
        if form.validate_on_submit():
            form = form.data['song']
            db.session.commit()
            return form.to_dict(), 200
        else:
            return jsonify(form.errors), 400

    else:
        res = {
            "message": "Song could not be found.",
            "statusCode": 404
        }
        return jsonify(res), 404

#delete a song
@songs_routes.route('/<int:id>/delete', methods=['DELETE'])
@login_required
def delete_song(id):
    song = Song.query.get(id)
    if song and current_user.id == song.user_id:
        db.session.delete(song)
        db.session.commit()
        res = {
            "id": song.id,
            "message": "Successfully deleted",
            "statusCode": 200
        }
        return jsonify(res), 200
    else:
        res = {
            "message": "Song couldn't be found",
            "statusCode": 404
        }
        return jsonify(res), 404

#view comments by Song ID
@songs_routes.route('/<int:id>/comments', methods=['GET'])
def view_song_by_comment_id(id):
    song = Song.query.get(id)
    if song is None:
        return jsonify({'error': 'Song not found'}), 404

    comments = song.comments
    comment_list = [comment.to_dict() for comment in comments]

    return jsonify(comment_list), 200

#create new song comment
@songs_routes.route('/<int:id>/comments/new', methods=['POST'])
@login_required
def new_comment(id):
    song = Song.query.get(id)
    if(song):
        form = CommentForm()
        form['csrf_token'].data = request.cookies['csrf_token']
        if form.validate_on_submit():
            comment = Comment(
                user_id=current_user.id,
                song_id=id,
                comment=form.comment.data
            )
            db.session.add(comment)
            db.session.commit()
            return comment.to_dict(), 200
        else:
            return jsonify(form.errors), 400
    else:
        res = {
            "message": "Song could not be found.",
            "statusCode": 404
        }
        return jsonify(res), 404


#update comment
@songs_routes.route('/<int:id>/comments/<int:comment_id>', methods=['PUT'])
@login_required
def update_comment(id, comment_id):
    comment = Comment.query.get(comment_id)
    if comment is None:
        return jsonify({'error': 'Comment not found'}), 404

    if comment.user_id != current_user.id:
        return jsonify({'error': 'You do not have permission to update this comment'}), 403

    form = CommentForm()
    form.csrf_token.data = request.cookies['csrf_token']
    if form.validate_on_submit():
        comment.comment = form.comment.data
        db.session.commit()

        comment_dict = comment.to_dict()
        comment_dict['user'] = current_user.to_dict()

        return jsonify(comment_dict), 200
    else:
        return jsonify(form.errors), 400
# def update_comment(comment_id):
#     # need a form var here that invokes our form for updating comment
#     # need a line here for requesting csrf token
#     comment = Comment.query.get(comment_id)
#     user = User.query.get(current_user.id)
#     user = user.to_dict()
#     if comment.user_id == current_user.id:
#         # need an if statement here that checks validate_on_submit
#         # if form.validate_on_submit()
#         # comment.body = form.data['body']
#         db.session.comment()
#         comment_dict = comment.to_dict()
#         comment_dict['users'] = {
#             # this is where we add our key and values for user info
#         }
#         return comment_dict
#     return {
#         # validation error here if comment does not exist
#     }
#     #another return statement here if user does not own the comment


#delete comment
@songs_routes.route('/<int:id>/comments/<int:comment_id>/delete', methods=['DELETE'])
@login_required
def delete_comment(id, comment_id):
    comment = Comment.query.get(comment_id)
    if comment is None:
        return jsonify({'error': 'Comment not found'}), 404

    if comment.user_id != current_user.id:
        return jsonify({'error': 'You do not have permission to delete this comment'}), 403

    db.session.delete(comment)
    db.session.commit()

    return jsonify({'message': 'Comment deleted successfully'}), 200

#view likes by song Id
@songs_routes.route('/<int:id>/likes', methods=['GET'])
def view_likes_by_song_id(id):
    song = Song.query.get(id)
    if(song):
        likes = SongLike.query.filter(SongLike.song_id == id)
        return jsonify([like.to_dict() for like in likes]),200
    else:
        res = {
            "message": "Song could not be found.",
            "statusCode": 404
        }
        return jsonify(res), 404

# #view likes by song Id
# @songs_routes.route('/<int:id>/likes', methods=['GET'])
# def song_likes(id):
#     song = Song.query.get(id)
#     if(song):
#         # Get all the likes from the database
#         comments = Comment.query.filter_by(song_id=id).all()
#         res = {
#             "message": "Successfully retrieved",
#             "statusCode": 200,
#             "comments": comments.to_dict()
#         }
#         return jsonify(res), 200
#     else:
#         res = {
#             "message": "Song could not be found.",
#             "statusCode": 404
#         }
#         return jsonify(res), 404

#create a new like
@songs_routes.route('/<int:id>/likes/new', methods=['POST'])
def create_like(id):
    user_id = current_user.id
    new_like = SongLike(user_id=user_id, song_id=id)
    db.session.add(new_like)
    db.session.commit()
    return jsonify(new_like.to_dict()), 201

#delete a like
@songs_routes.route('/<int:id>/likes/<int:like_id>/delete', methods=['DELETE'])
def delete_like(id, like_id):
    like = SongLike.query.get(like_id)
    if like is None:
        return jsonify({'error': 'Like not found'}), 404

    if like.user_id != current_user.id:
        return jsonify({'error': 'You do not have permission to delete this like'}), 403

    db.session.delete(like)
    db.session.commit()

    return jsonify({'message': 'Like deleted successfully'}), 200
