import { useState, useLayoutEffect } from 'react';
import type { RefObject } from 'react';

export type HeaderState = {
    paddingPx: number;
    layoutType: 'absolute-center' | 'flex-center';
    showOrgName: boolean;
    showDesktopMenu: boolean;
};

export function useHeaderLayout(
    containerRef: RefObject<HTMLElement | null>,
    ghostContainerRef: RefObject<HTMLDivElement | null>,
    logoFullRef: RefObject<HTMLDivElement | null>,
    logoSmallRef: RefObject<HTMLDivElement | null>,
    desktopMenuRef: RefObject<HTMLUListElement | null>,
    mobileMenuRef: RefObject<HTMLDivElement | null>,
    rightControlsRef: RefObject<HTMLDivElement | null>,
    minGap: number,
    paddingNormal: number,
    paddingMinimal: number
): HeaderState {
    const [state, setState] = useState<HeaderState>({
        paddingPx: paddingNormal, layoutType: 'absolute-center', showOrgName: true, showDesktopMenu: true,
    });

    useLayoutEffect(() => {
        const updateLayout = () => {
            if (!containerRef.current || !logoFullRef.current || !logoSmallRef.current ||
                !desktopMenuRef.current || !rightControlsRef.current || !mobileMenuRef.current) return;

            const W = containerRef.current.getBoundingClientRect().width;
            const L_full = logoFullRef.current.getBoundingClientRect().width;
            const L_small = logoSmallRef.current.getBoundingClientRect().width;
            const M_desk = desktopMenuRef.current.getBoundingClientRect().width;
            const M_mob = mobileMenuRef.current.getBoundingClientRect().width;
            const R = rightControlsRef.current.getBoundingClientRect().width;

            const center = W / 2;
            const menuLeftAbs = center - M_desk / 2;
            const menuRightAbs = center + M_desk / 2;

            if (menuLeftAbs >= paddingNormal + L_full + minGap && (W - menuRightAbs) >= paddingNormal + R + minGap) {
                setState({ paddingPx: paddingNormal, layoutType: 'absolute-center', showOrgName: true, showDesktopMenu: true });
            }
            else if (menuLeftAbs >= paddingMinimal + L_full + minGap && (W - menuRightAbs) >= paddingMinimal + R + minGap) {
                setState({ paddingPx: paddingMinimal, layoutType: 'absolute-center', showOrgName: true, showDesktopMenu: true });
            }
            else if (W >= 2 * paddingMinimal + L_full + R + M_desk + 2 * minGap) {
                setState({ paddingPx: paddingMinimal, layoutType: 'flex-center', showOrgName: true, showDesktopMenu: true });
            }
            else if (W >= 2 * paddingMinimal + L_small + R + M_desk + 2 * minGap) {
                setState({ paddingPx: paddingMinimal, layoutType: 'flex-center', showOrgName: false, showDesktopMenu: true });
            }
            else if (W >= 2 * paddingMinimal + L_full + R + M_mob + 2 * minGap) {
                setState({ paddingPx: paddingMinimal, layoutType: 'flex-center', showOrgName: true, showDesktopMenu: false });
            }
            else {
                setState({ paddingPx: paddingMinimal, layoutType: 'flex-center', showOrgName: false, showDesktopMenu: false });
            }
        };

        const ro = new ResizeObserver(() => updateLayout());
        if (containerRef.current) ro.observe(containerRef.current);
        if (ghostContainerRef.current) ro.observe(ghostContainerRef.current);

        updateLayout();
        return () => ro.disconnect();
    }, [minGap, paddingNormal, paddingMinimal, containerRef, ghostContainerRef, logoFullRef, logoSmallRef, desktopMenuRef, mobileMenuRef, rightControlsRef]);

    return state;
}