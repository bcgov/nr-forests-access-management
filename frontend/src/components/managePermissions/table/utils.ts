import { router } from "@/router";
import { selectedApplicationId } from "@/store/ApplicationState";
import { UserDetailsRoute } from "@/router/routes";

export const navigateToUserDetails = (userId: string) => {
    router.push({
        name: UserDetailsRoute.name,
        params: {
            applicationId: selectedApplicationId.value,
            userId,
        },
    });
};
