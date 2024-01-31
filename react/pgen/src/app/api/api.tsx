'use server'

import { cookies, headers } from 'next/headers'
import { redirect } from 'next/navigation';
import { paths } from './api-definition';

export type StateType = {object: {[x: string]: any}, errors: {[x: string]: string}, status: number}

const API_URL = "http://python:5000"
const LOGIN = '/login'
const FORBBIDEN = '/forbidden'
const NOT_FOUND = '/not-found'
const ERROR_INESPERADO = '/error-inesperado'
export const authorizationTokenCookieName = () => {
  return 'authorizationToken'
}

type Path = keyof paths;
type PathMethod<P extends Path> = keyof paths[P];

type RequestParams<P extends Path, M extends PathMethod<P>> = paths[P][M] extends {
  parameters: {path: any};
}
  ? paths[P][M]['parameters']['path']
  : undefined;

type RequestBody<P extends Path, M extends PathMethod<P>> = paths[P][M] extends {
  requestBody: { content: any };
}
  ? paths[P][M]['requestBody']['content']['application/json']
  : undefined;

type ResponseType<P extends Path, M extends PathMethod<P>> = paths[P][M] extends {
  responses: { [code: number]: any };
}
  ? paths[P][M]['responses']
  : undefined;

class ApiCall <P extends Path, M extends PathMethod<P>> {
  url: P;
  method: M;
  params: RequestParams<P, M> extends undefined ? {} : RequestParams<P, M>;
  body: RequestBody<P, M> extends undefined ? {} : RequestBody<P, M>;

  constructor(
    url: P,
    method: M,
    params: RequestParams<P, M> extends undefined ? {} : RequestParams<P, M>,
    body: RequestBody<P, M> extends undefined ? {} : RequestBody<P, M>) {

      this.url = url;
      this.method = method;
      this.params = params;
      this.body = body;

  }

  async fetch(tags: string[]): Promise<ResponseType<P, M>> {
    const cookieStore: any = cookies()

    let urlWithParams = API_URL + this.url;
    for (const key in this.params) {
      urlWithParams = urlWithParams.replace(`{${key}}`, this.params[key].toString());
    }
    
    let options: any = {
      method: this.method.toString(),
      cache: 'no-store',
      // TODO: hay que meterlo en la sesión
      headers: { 'Content-Type': 'application/json', 'Authorization': cookieStore.get(authorizationTokenCookieName())?.value ?? '' }
    };

    if (tags.length !== 0) {
      options.next = {tags: tags}
    }

    if (this.method.toString().toLowerCase() !== 'get') {
      options.body = JSON.stringify(this.body);
    }

    const res = await fetch(urlWithParams, options);
    const status: number = res.status;
    const response: any = {}
    response[status] = {
      'content': {
        'application/json': await res.json()
      }
    }
    return response;
  }

}

type ResponseHandlerType<P extends Path, M extends PathMethod<P>> = {
  [code in keyof ResponseType<P, M>]?: (response: ResponseType<P, M>) => StateType
}

class ApiCallHandlerClass <P extends Path, M extends PathMethod<P>> {
  api: ApiCall<P, M>;
  response: ResponseType<P, M> | null;
  responsesHandler: ResponseHandlerType<P, M>;

  constructor (
    url: P,
    method: M,
    params: RequestParams<P, M> extends undefined ? {} : RequestParams<P, M>,
    body: RequestBody<P, M> extends undefined ? {} : RequestBody<P, M>) {

      this.api = new ApiCall(url, method, params, body);
      this.response = null;
      this.responsesHandler = {};
  }

  async fetch(tags: string[] = []): Promise<StateType> {
    'use server'
    this.response = await this.api.fetch(tags);
    if (this.response === undefined) {
      redirect(ERROR_INESPERADO)
    }

    // Siempre va a haber uno o ningún elemento en la unión
    const union = Object.keys(this.response).filter(code => Object.keys(this.responsesHandler).includes(code))

    const responseCodeInHandler: boolean = union.length > 0;
    if (responseCodeInHandler) {
      // @ts-ignore
      return this.responsesHandler[union[0]](this.response)
    }

    if (this.response[200]) {
      return {
        object: this.response[200].content["application/json"],
        errors: {},
        status: 200
      }
    }

    if (this.response[201]) {
      return {
        object: this.response[201].content["application/json"],
        errors: {},
        status: 201
      }
    }

    if (this.response[400]) {
      return {
        object: {},
        errors: this.response[400].content["application/json"],
        status: 400
      }
    }

    if (this.response[401]) {
      const current_url = headers().get('x-path') ?? '/'
      return redirect(LOGIN + '?callback=' + current_url)
    }

    if (this.response[403]) {
      return redirect(FORBBIDEN)
    }

    if (this.response[404]) {
      return redirect(NOT_FOUND)
    }

    if (this.response[500]) {
      console.log(this.response[500])
      return redirect(ERROR_INESPERADO)
    }

    return redirect(ERROR_INESPERADO)
  }

  onResponse = (responsesHandler: ResponseHandlerType<P, M>): ApiCallHandlerClass<P,M> => {
    this.responsesHandler = responsesHandler;
    return this;
  }
}

export const ApiCallHandler = <P extends Path, M extends PathMethod<P>> (
    url: P,
    method: M,
    params: RequestParams<P, M> extends undefined ? {} : RequestParams<P, M>,
    body: RequestBody<P, M> extends undefined ? {} : RequestBody<P, M>): ApiCallHandlerClass<P,M> => {
  return new ApiCallHandlerClass(url, method, params, body);
}

