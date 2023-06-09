import React, { useState } from "react";
import { useDispatch} from "react-redux";
import { useModal } from "../../context/Modal";
import PropTypes from 'prop-types';
import * as CommentActions from "../../store/comments";
import "./CreateComment.css";

function CreateCommentModal({ songId, onCommentSubmit }) {
    const dispatch = useDispatch();

    const [comment, setComment] = useState("");
    const [errors, setErrors] = useState("");
    const [refreshKey, setRefreshKey] = useState(0);
    const { closeModal } = useModal();


    const handleSubmit = async (e) => {
        e.preventDefault();
        setErrors([]);
        const data = await dispatch(CommentActions.createCommentThunk(songId, comment))
        setComment("");

        if (data && !data.errors) {
            closeModal();
            onCommentSubmit();
            dispatch(CommentActions.getAllCommentsBySongThunk(songId));
            setRefreshKey(prevKey => prevKey + 1);
        } else if (data.errors) {
            setErrors(data.errors);
        }

    }

    return (
        <>
            <div className="create-comment-modal">
                <h1 id='login-text'>Comment</h1>
                <form onSubmit={handleSubmit}>
                    <div className="create-comment-form">
                        <label id='username-email'>
                            <textarea
                                value={comment}
                                onChange={(e) => setComment(e.target.value)}
                                rows={2}
                                required
                                placeholder="Comment"
                            ></textarea>
                            <button type='submit'>Submit</button>
                        </label>
                    </div>
                </form>
            </div>
        </>
    )
}

CreateCommentModal.propTypes = {
    songId: PropTypes.string.isRequired,
    onCommentSubmit: PropTypes.func.isRequired
}

export default CreateCommentModal
