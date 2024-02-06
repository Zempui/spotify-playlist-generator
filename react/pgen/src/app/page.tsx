'use server'

import { cookies } from "next/headers";
import ClientComponent from "./clientComponent";

export default async function Home() {
  const cookieStore = cookies();
  const session: string = cookieStore.get('session')?.value ?? '';
  const loggedIn = session !== '';

  return (
    <>
    <ClientComponent loggedIn={loggedIn}/>
    </>
  );
}
