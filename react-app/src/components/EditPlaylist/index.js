import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import * as PlaylistActions from '../../store/playlists';
import * as SongActions from '../../store/songs';
import { useHistory } from 'react-router-dom';

import './EditPlaylist.css';

const EditPlaylistModal = ({ playlistId, closeModal, setRefresh }) => {
    const dispatch = useDispatch();
    const user = useSelector((state) => state.session.user);
    const playlists = useSelector((state) => state.playlists.playlists);
    const songs = useSelector((state) => Object.values(state.songs.songs));
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [selectedSongs, setSelectedSongs] = useState([]);
    const [errors, setErrors] = useState({});
    const history = useHistory();

    useEffect(() => {
        dispatch(SongActions.getAllSongsThunk());
    }, [dispatch]);

    const handleSubmit = async (e) => {
        e.preventDefault();

        const newErrors = {};

        if (!name || name.trim() === '') {
        newErrors.name = 'Name cannot be empty.';
        }
        if (!description || description.trim() === '') {
        newErrors.description = 'Description cannot be empty.';
        }
        if (Object.keys(newErrors).length > 0) {
        setErrors(newErrors);
        return; // Return early if there are errors
        }

        const payload = {
        id: playlistId,
        name,
        description,
        songs: selectedSongs,
        };

        const data = await dispatch(
        PlaylistActions.updatePlaylistThunk(user.id, payload)
        );

        if (data) {
        const playlistId = data.id;
        if (playlistId && selectedSongs.length > 0) {
            for (const songId of selectedSongs) {
            const songPayload = {
                songId,
            };
            await dispatch(
                PlaylistActions.addSongToPlaylistThunk(playlistId, songPayload)
            );
            }
        }
        const url = `/users/${user.id}/playlists`;
        closeModal();
        history.push(url);
        }
    };

    const handleDeleteSong = async (songId) => {
        await dispatch(PlaylistActions.deleteSongFromPlaylistThunk(playlistId, songId));

        const updatedSelectedSongs = selectedSongs.filter((id) => id !== songId);
        setSelectedSongs(updatedSelectedSongs);
        setRefresh((refresh) => !refresh);
        closeModal();
    };

    const handleCancel = () => {
        closeModal();
    };

    useEffect(() => {
        const fetchPlaylist = async () => {
        const data = await dispatch(PlaylistActions.getPlaylistThunk(playlistId));
        if (data) {
            setName(data.name);
            setDescription(data.description);
            setSelectedSongs(data.songs);
        }
        };
        fetchPlaylist();
        dispatch(SongActions.getAllSongsThunk());
    }, [dispatch, playlistId]);

    return (
        <div className="edit-playlist-modal-overlay">
        <div className="edit-playlist-modal">
            <form className="edit-playlist-form" onSubmit={handleSubmit}>
            <h2>Edit Playlist</h2>
            {Object.keys(errors).length > 0 && (
                <ul className="errors">
                {Object.values(errors).map((error, index) => (
                    <li key={index}>{error}</li>
                ))}
                </ul>
            )}
            <div className="form-group">
                <label htmlFor="name">Name</label>
                <input
                type="text"
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                />
            </div>
            <div className="form-group">
                <label htmlFor="description">Description</label>
                <textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                />
            </div>
            <div className="form-group">
                <button type="submit">Update</button>
                <button type="button" onClick={handleCancel}>
                Cancel
                </button>
            </div>
            <div className="form-group">
                <label htmlFor="songs">Select Songs</label>
                <select
                id="songs"
                value={selectedSongs}
                onChange={(e) =>
                    setSelectedSongs(
                    Array.from(e.target.selectedOptions, (option) => option.value)
                    )
                }
                multiple
                >
                {songs.map((song) => (
                    <option key={song.id} value={song.id}>
                    {song.name}
                    </option>
                ))}
                </select>
            </div>
            </form>
            <div className="browse-songs">
            <h3>Browse Songs in Playlist</h3>
            {playlists.user[playlistId].songs.map((song) => (
                <div key={song.id}>
                <p>{song.name}</p>
                <button onClick={() => handleDeleteSong(song.id)}>
                    Delete Song
                </button>
                </div>
            ))}
            </div>
        </div>
        </div>
    );
};

export default EditPlaylistModal;
