'use server'

import { redirect } from "next/navigation";
import { ApiCallHandler } from "../api/api";

export const loginAction = async (revState: {[x: string]: any}, formData: FormData): Promise<{[x: string]: any}> => {

    const apiCall = ApiCallHandler('/login', 'get', {}, {})
        .onResponse({
            200(response) {
                redirect(response[200].schema?.auth_url ?? '/error-inserperado')
            },
        })
    
    await apiCall.fetch()
    return revState;
}

export const searchAction = async (revState: {[x: string]: any}, formData: FormData): Promise<{[x: string]: any}> => {

    const query: string = formData.get('query')?.toString() ?? '';

    if (query.trim() === '') {
        revState.object = [];
        return revState;
    }

    const apiCall = ApiCallHandler('/search_artist/{query}', 'get', {query: query}, {})
        .onResponse({
            200(response) {
                return {
                    object: Array.isArray(response[200].schema) ? response[200].schema : revState.object,
                    error: '',
                    status: 200
                }
            },
        })
    
    return await apiCall.fetch();
}

export const createPlaylistAction = async (revState: {[x: string]: any}, formData: FormData): Promise<{[x: string]: any}> => {
    const selectedArtistsJSON = formData.get('selectedArtists') as string;
    const selectedArtists = JSON.parse(selectedArtistsJSON).map((value: any) => value.name);
    const playlistName = formData.get('playlistName') as string;

    const apiCall = ApiCallHandler('/create_playlist', 'post', {}, {artists: selectedArtists, name: playlistName})
    
    const res = await apiCall.fetch();
    return revState;
}