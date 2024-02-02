'use server'

import { cookies } from "next/headers";
import ClientComponent from "./clientComponent";

export default async function Home() {
  const cookieStore = cookies();
  const code: string = cookieStore.get('code')?.value ?? '';
  const loggedIn = code !== '';

  return (
    <>
    <ClientComponent loggedIn={loggedIn}/>
    </>
  );
}
