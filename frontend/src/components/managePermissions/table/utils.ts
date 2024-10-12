import { router } from "@/router";
import { selectedApplicationId } from "@/store/ApplicationState";

export const navigateToUserDetails = (userId: string) => {
    router.push({
        name: "UserDetails",
        params: {
            applicationId: selectedApplicationId.value,
            userId,
        },
    });
};
