'use client'

type Props = {searchParams: {code?: string}};
export default function Callback({searchParams: {code}}: Props) {
  console.log(code)
  return (
    <>
    </>
  );
}
