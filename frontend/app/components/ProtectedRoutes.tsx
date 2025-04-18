import { useEffect } from "react";
import { useRouter } from "next/router";
import { useAuthContext } from "../hooks/useAuth";

export const ProtectedRoute = ({children} : {children: React.ReactNode}) => {
    const { user } = useAuthContext();
    const router = useRouter();

    useEffect(() => {
        if (!user) {
            router.push("/login");
        }
    }, [user, router]);

    return user ? children : null;
}
