import { browser } from '$app/environment';

export default async function useFetch(url: string, options?: RequestInit): Promise<Response> {
    if (browser) {
        let token = localStorage.getItem('token') || '';

        const response = await fetch(url, { ...options, headers: { ...options?.headers, 'Authorization': token } });
        if (!response.ok) {
            localStorage.removeItem('token');
            throw new Error('Failed to fetch');
        }
        return response.json();
    }
}
