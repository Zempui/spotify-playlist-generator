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